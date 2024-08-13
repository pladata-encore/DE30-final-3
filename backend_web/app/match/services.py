import os
import requests
import pandas as pd
import numpy as np
import pickle
import logging
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.base import BaseEstimator
from app.kafka.kafka_producer import send_to_matches
from app.kafka.kafka_producer import send_to_match_user


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def call_matches_api_by_match_id(shard, match_id):
    url = f"https://api.pubg.com/shards/{shard}/matches/{match_id}"
    headers = {
        "accept": "application/vnd.api+json",
    }

    matches_response = requests.get(url, headers=headers)

    return matches_response


def get_n_ranked_match_ids_from_seasonal_match_ids(shard, match_ids, n):
    ranked_match_ids = []
    count = 0
    for match_id in match_ids:
        if count == n:
            break
        else:
            if call_matches_api_by_match_id(shard, match_id).json()['data']['attributes']['matchType'] == 'competitive':
                ranked_match_ids.append(match_id)
                count += 1

    return ranked_match_ids


def call_preprocess_api_by_account_id_match_id_shard(account_id, match_id, shard):
    url = "http://10.11.10.180:8000/api/v1/preprocess"
    data = {
        "playerID": account_id,
        "matchID": match_id,
        "shardID": shard
    }
    headers = {
        "Content-Type": "application/json"
    }
    preprocess_response = requests.post(url, json=data, headers=headers)

    return preprocess_response


def clustering_belligerence_calc_statistics(preprocess_response):
    preprocess_result = preprocess_response.json()
    clustering_input_match_id = preprocess_result[2]['match_id']
    clustering_input_account_id = preprocess_result[1]['account_id']
    clustering_input_map_id = preprocess_result[2]['map_id']
    # clustering_input_total_shot = preprocess_result[1]['total_shots']
    clustering_input_players_data = preprocess_result[2]['players_data']

    df = pd.DataFrame(clustering_input_players_data)
    df['match_id'] = clustering_input_match_id
    df.rename(columns={
        'landing_coordinates_x': 'landed_location_x',
        'landing_coordinates_y': 'landed_location_y'
    }, inplace=True)

    # Map Y 오프셋 정의
    map_y_offsets = {
        'Desert_Main': 816000,
        'Baltic_Main': 816000,
        'DihorOtok_Main': 816000,
        'Erangel_Main': 816000,
        'Tiger_Main': 816000,
        'Neon_Main': 816000,
        'Savage_Main': 408000,
        'Chimera_Main': 306000,
        'Summerland_Main': 204000,
        'Heaven_Main': 102000
    }

    # 데이터 전처리
    df.dropna(inplace=True)
    df['landed_location_x'] = df['landed_location_x'].astype(float)
    df['landed_location_y'] = df['landed_location_y'].astype(float)

    # landed_location_y 변환
    df['landed_location_y'] = df.apply(
        lambda row: map_y_offsets.get(clustering_input_map_id, 816000) - abs(row['landed_location_y']), axis=1
    )

    xy_values = df[['landed_location_x', 'landed_location_y']].values
    scaler = StandardScaler()
    xy_values_scaled = scaler.fit_transform(xy_values)

    # 데이터 포인트 수 확인
    n_samples = len(xy_values_scaled)
    if n_samples < 4:
        return {'message': f"Match ID: {clustering_input_match_id} has too few data points to cluster. Skipping..."}

    max_clusters = min(10, n_samples)  # 데이터 포인트 수보다 클러스터 수가 많아지지 않도록 설정

    # 최적의 클러스터 수 찾기
    silhouette_scores = []
    for k in range(4, max_clusters + 1):  # 최소 4개에서 최대 클러스터 개수
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(xy_values_scaled)
        labels = kmeans.labels_

        # 레이블이 1개 이하인 경우 silhouette score를 계산하지 않음
        if len(set(labels)) > 1:
            silhouette_avg = silhouette_score(xy_values_scaled, labels)
            silhouette_scores.append((k, silhouette_avg))

    if not silhouette_scores:
        return {'message': f"Match ID: {clustering_input_match_id} has too few data points to cluster. Skipping..."}

    # 최적의 클러스터 수로 클러스터링 수행
    optimal_k = max(silhouette_scores, key=lambda x: x[1])[0]
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    df['cluster'] = kmeans.fit_predict(xy_values_scaled)

    # 클러스터 점수 계산 및 호전성 점수 계산
    cluster_counts = df['cluster'].value_counts().to_dict()
    df['cluster_score'] = df['cluster'].map(cluster_counts)
    df['belligerence'] = df['cluster_score'] * 20 + df['total_shots']
    df['belligerence'] = df['belligerence'].astype(float)

    # 매치별 평균 호전성 및 표준편차 계산
    belligerence_avg = df['belligerence'].mean()
    belligerence_std = df['belligerence'].std()

    matches_key = {
        "match_id": preprocess_result[0]['match_id']
    }
    matches_value = preprocess_result[0]
    matches_value['belligerence_avg'] = belligerence_avg
    matches_value['belligerence_std'] = belligerence_std
    send_to_matches(matches_key, matches_value)

    match_user_key = {
        "account_id": preprocess_result[1]['account_id'],
        "match_id": preprocess_result[1]['match_id']
    }

    match_user_value = preprocess_result[1]
    match_user_value['belligerence'] = df.loc[df['account_id'] == clustering_input_account_id, 'belligerence'].values[0]
    send_to_match_user(match_user_key, match_user_value)

    response_body = {
        "match_data": matches_value,
        "match_user_data": match_user_value
    }

    return response_body


def call_ml_speed_data_api_by_account_id_match_id_shard(account_id, match_id, shard):
    url = "http://10.11.10.180:8000/api/v1/speed"
    data = {
        "playerID": account_id,
        "matchID": match_id,
        "shardID": shard
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        ml_speed_data_response = requests.post(url, json=data, headers=headers)
        ml_speed_data_response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        logging.info(f"API call successful for account_id: {account_id}, match_id: {match_id}, shard: {shard}")
        return ml_speed_data_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        return None


def speed_ml_data_type_check(data):
    data_1 = data.get("speed_hack",{})
    for item in data_1:
        # print("컬럼명 변경 감지")
        if 'km/h' in item:
            item['km_per_h'] = item.pop('km/h')
        else:
            continue
    return data_1


# 특정 유저의 비정상적인 스피드를 예측하는 함수
def predict_speed_outliers_for_user(account_id, walk_model_path, vehicle_model_directory, data):
    # 유저의 데이터 로드
    # df = get_user_data(account_id)
    df = pd.DataFrame(data)
    if df.empty:
        print(f"No data found for account_id {account_id}.")
        return

    predictions = {}

    # 워크 로그 처리
    walk_df = df[df['vehicle_id'] == 'walk'].copy()
    if not walk_df.empty:
        if os.path.exists(walk_model_path):
            with open(walk_model_path, 'rb') as f:
                model, scaler = pickle.load(f)

            # 데이터 정규화 및 예측
            print(model, type(model), "##################################################")
            X_scaled = scaler.transform(walk_df[['km_per_h', 'time_diff']])
            walk_df.loc[:, 'cluster'] = model.predict(X_scaled)

            # 클러스터 중심에서의 거리 계산
            centers = model.cluster_centers_
            walk_df.loc[:, 'distance_to_center'] = [
                np.linalg.norm(X_scaled[idx] - centers[cluster])
                for idx, cluster in enumerate(walk_df['cluster'])
            ]

            # Z-Score 계산
            mean_distance = walk_df['distance_to_center'].mean()
            std_distance = walk_df['distance_to_center'].std()
            z_score_threshold = 3
            walk_df.loc[:, 'z_score'] = (walk_df['distance_to_center'] - mean_distance) / std_distance
            walk_df.loc[:, 'is_outlier'] = walk_df['z_score'].abs() > z_score_threshold

            predictions['walk'] = walk_df[['account_id', 'vehicle_id', 'km_per_h', 'is_outlier']]
        else:
            print("Walk model file not found.")

        # 차량 로그 처리
    vehicle_df = df[df['vehicle_id'] != 'walk']
    for vehicle_id, group_df in vehicle_df.groupby('vehicle_id'):
        model_path = os.path.join(vehicle_model_directory, f'{vehicle_id}_model.pkl')

        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model, scaler = pickle.load(f)
            print(model,type(model),"##################################################")
            # 데이터 정규화 및 예측
            X_scaled = scaler.transform(group_df[['km_per_h', 'time_diff']])
            group_df['cluster'] = model.predict(X_scaled)

            # 클러스터 중심에서의 거리 계산
            centers = model.cluster_centers_
            group_df['distance_to_center'] = [
                np.linalg.norm(X_scaled[idx] - centers[cluster])
                for idx, cluster in enumerate(group_df['cluster'])
            ]

            # Z-Score 계산
            mean_distance = group_df['distance_to_center'].mean()
            std_distance = group_df['distance_to_center'].std()
            z_score_threshold = 3
            group_df['z_score'] = (group_df['distance_to_center'] - mean_distance) / std_distance
            group_df['is_outlier'] = group_df['z_score'].abs() > z_score_threshold

            predictions[vehicle_id] = group_df[['account_id', 'vehicle_id', 'km_per_h', 'is_outlier']]
        else:
            print(f"표본이 너무 적어서 {vehicle_id}의 예측을 수행할 수 없습니다.")

    return predictions



def call_ml_shot_data_api_by_account_id_match_id_shard(account_id, match_id, shard):
    url = "http://10.11.10.180:8000/api/v1/shot"
    data = {
        "playerID": account_id,
        "matchID": match_id,
        "shardID": shard
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        ml_shot_data_response = requests.post(url, json=data, headers=headers)
        ml_shot_data_response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        logging.info(f"API call successful for account_id: {account_id}, match_id: {match_id}, shard: {shard}")
        return ml_shot_data_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        return None


def load_shot_ml_model_from_directory_by_tier(model_dir_path, tier):
    file_name = 'kmeans_model_tier_' + tier + '.pkl'
    model_path = os.path.join(model_dir_path, file_name)

    # 모델이 존재하는지 확인
    if not os.path.exists(model_path):
        return -1

    # pickle을 사용하여 모델을 로드
    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    return model


def parse_shot_data_run_ml(data, model):
    kmeans_model = model['kmeans_model']
    scaler = model['scaler']
    pca = model['pca']
    max_distances = model['max_distances']
    centers = model['centers']

    # 각 값을 리스트로 감싸기
    parsed_data = {
        'kills': [data['for_ml_user']['kills']],
        'knockdowns': [data['for_ml_user']['knockdowns']],
        'assists': [data['for_ml_user']['assists']],
        'total_damage': [data['for_ml_user']['total_damage']],
        'total_shot': [data['for_ml_user']['total_shot']],
        'hit_count': [data['for_ml_user']['hit_count']],
        'head_shot': [data['for_ml_user']['head_shot']]
    }

    df = pd.DataFrame(parsed_data)

    # 명중률과 헤드샷 명중률 계산
    df['hit_rate'] = df['hit_count'] / df['total_shot'] * 100
    df['headshot_rate'] = df['head_shot'] / df['total_shot'] * 100

    # 저장된 Scaler와 PCA 모델을 사용하여 새로운 데이터에 동일한 전처리 적용
    scaled_features = scaler.transform(
        df[["hit_rate", "kills", "knockdowns", "assists", "total_damage", "headshot_rate", "total_shot"]])
    pca_features = pca.transform(scaled_features)
    df['pca_one'] = pca_features[:, 0]
    df['pca_two'] = pca_features[:, 1]

    # 클러스터 예측
    df['cluster'] = kmeans_model.predict(df[['pca_one', 'pca_two']])

    # 클러스터 중심과 새로운 데이터 포인트 사이의 거리 계산
    centers = kmeans_model.cluster_centers_
    df['distance_to_center'] = df.apply(
        lambda row: np.linalg.norm([row['pca_one'], row['pca_two']] - centers[int(row['cluster'])]),
        axis=1
    )

    # 새로운 데이터가 이상치인지 판단
    df['is_outlier'] = df.apply(
        lambda row: row['distance_to_center'] > max_distances[int(row['cluster'])],
        axis=1
    )

    result = {
        "account_id": data['for_ml_user']['account_id'],
        "match_id": data['for_ml_user']["match_id"],
        "cluster": int(df.loc[0, 'cluster']),
        "pca_one": df['pca_one'].tolist()[0],
        "pca_two": df['pca_two'].tolist()[0],
        "distance_to_center": float(df.loc[0, 'distance_to_center']),
        "is_outlier": bool(df.loc[0, 'is_outlier']),
        "centers": centers.tolist(),
        "max_distances": max_distances
    }

    return result
