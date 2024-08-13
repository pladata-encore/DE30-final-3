from flask import session, jsonify, request
from app import redis_client
from app.match import match
from app.match.services import call_preprocess_api_by_account_id_match_id_shard
from app.match.services import clustering_belligerence_calc_statistics
from app.match.services import call_ml_speed_data_api_by_account_id_match_id_shard
from app.match.services import get_n_ranked_match_ids_from_seasonal_match_ids
from app.match.services import speed_ml_data_type_check
from app.match.services import predict_speed_outliers_for_user
from app.match.services import call_ml_shot_data_api_by_account_id_match_id_shard
from app.match.services import load_shot_ml_model_from_directory_by_tier
from app.match.services import parse_shot_data_run_ml
from app.kafka.kafka_producer import send_to_clustering_input
from app.kafka.kafka_producer import send_to_matches
from app.kafka.kafka_producer import send_to_match_user
import uuid
import time
import json


@match.route('/filterrankedmatches', methods=['POST'])
def filter_ranked_match_id():
    input_body = request.json
    response = {"body": get_n_ranked_match_ids_from_seasonal_match_ids(input_body['shard'], input_body['match_ids'], input_body['n'])}

    return jsonify(response), 200


@match.route('/process/<shard>/<account_id>/<match_id>', methods=['GET'])
def process_matches_match_user(shard, account_id, match_id):
    preprocess_response = call_preprocess_api_by_account_id_match_id_shard(account_id, match_id, shard)
    if preprocess_response.status_code != 200:
        return jsonify({"message": "preprocess server error."}), 400

    else:
        response_body = clustering_belligerence_calc_statistics(preprocess_response)
        return jsonify(response_body), 200


@match.route('/overwatch/speed/<shard>/<account_id>/<match_id>', methods=['GET'])
def overwatch_speed(shard, account_id, match_id):
    response = call_ml_speed_data_api_by_account_id_match_id_shard(account_id, match_id, shard)
    walk_model_path = "/home/ec2-user/web-backend/app/models/vehicle/walk_model.pkl"  # walk pkl 파일 명시
    vehicle_model_directory = "/home/ec2-user/web-backend/app/models/vehicle"  # pkl 파일이 위치한 디렉토리

    checked_speed_json = speed_ml_data_type_check(response)

    if ('/'.join(walk_model_path.split("/")[:-1]) != vehicle_model_directory) or (
    not walk_model_path.endswith(".pkl")) or (
            vehicle_model_directory != "/home/ec2-user/web-backend/app/models/vehicle"):
        print("File path error")
    else:
        predictions = predict_speed_outliers_for_user(account_id, walk_model_path, vehicle_model_directory, checked_speed_json)
        # 예측 결과 출력
        if predictions:
            prediction_results = []
            for vehicle_id, result_df in predictions.items():
                for _, row in result_df.iterrows():
                    status = 'Outlier' if row['is_outlier'] else 'Normal'
                    prediction_results.append({
                        "account_id": row['account_id'],
                        "km_per_h": row['km_per_h'],
                        "status": status
                    })
        else:
            prediction_results = [{"message": "No predictions available."}]

    response_body = {
        "predictions": prediction_results,
        "xy_location": response['xy_location']
    }

    return jsonify(response_body), 200


@match.route('/overwatch/shot/<shard>/<account_id>/<match_id>', methods=['GET'])
def overwatch_shot(shard, account_id, match_id):
    response = call_ml_shot_data_api_by_account_id_match_id_shard(account_id, match_id, shard)
    model_directory = "/home/ec2-user/web-backend/app/models/aim/"
    model = load_shot_ml_model_from_directory_by_tier(model_directory, response['for_ml_user']['current_tier'])
    result = parse_shot_data_run_ml(response, model)
    response_body = {'result': result}

    return jsonify(response_body), 200


@match.route('/sparkprocess/<shard>/<account_id>/<match_id>', methods=['GET'])
def spark_test(shard, account_id, match_id):
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        print(f"created session: {session['session_id']}.")

    preprocess_result = call_preprocess_api_by_account_id_match_id_shard(account_id, match_id, shard)
    if preprocess_result.status_code != 200:
        return jsonify({"message": "preprocess server error."}), 400

    preprocess_result = preprocess_result.json()
    session_id = session['session_id']
    clustering_input_match_id = preprocess_result[2]['match_id']
    clustering_input_account_id = preprocess_result[1]['account_id']
    clustering_input_map_id = preprocess_result[2]['map_id']
    clustering_input_players_data = preprocess_result[2]['players_data']
    clustering_input_key = {
        "session_id": session_id
    }
    clustering_input_value = {
        "match_id": clustering_input_match_id,
        "account_id": clustering_input_account_id,
        "map_id": clustering_input_map_id,
        "players_data": clustering_input_players_data
    }

    send_to_clustering_input(clustering_input_key, clustering_input_value)

    timeout = 300
    start_time = time.time()
    clustering_output = None
    while time.time() - start_time < timeout:
        clustering_output = redis_client.get(session_id)
        if clustering_output:
            redis_client.delete(session_id)
            clustering_output = json.loads(clustering_output)
            break
        time.sleep(1)

    print(clustering_output)
    if clustering_output:
        matches_key = {
            "match_id": preprocess_result[0]['match_id']
        }
        matches_value = preprocess_result[0]
        matches_value['belligerence_avg'] = clustering_output['belligerence_avg']
        matches_value['belligerence_std'] = clustering_output['belligerence_std']
        send_to_matches(matches_key, matches_value)

        match_user_key = {
            "account_id": preprocess_result[1]['account_id'],
            "match_id": preprocess_result[1]['match_id']
        }

        match_user_value = preprocess_result[1]
        match_user_value['belligerence'] = clustering_output['belligerence']
        send_to_match_user(match_user_key, match_user_value)

        response = {
            "match_data": matches_value,
            "match_user_data": match_user_value
        }
        return jsonify(response), 200

    else:
        return jsonify({"message": "error"}), 400
