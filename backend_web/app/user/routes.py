from flask import jsonify
import mysql.connector
import json
from app import redis_client
from app.user import user
from app.user.services import check_api_server
from app.user.services import call_players_api_by_nickname
from app.user.services import get_account_id_from_players_api_response
from app.user.services import get_shard_from_players_api_response
from app.user.services import call_ranked_stats_api_by_account_id
from app.user.services import jsonify_ranked_stats_from_api
from app.user.services import get_match_id_list_from_players_api_response
from app.kafka.kafka_producer import send_to_users


@user.route('/<shard>/<nickname>', methods=['GET'])
def search(shard, nickname):
    squad_statistics = redis_client.get('squad')
    squad_statistics = json.loads(squad_statistics.decode('utf-8')) if squad_statistics else None
    
    squad_fpp_statistics = redis_client.get('squad-fpp')
    squad_fpp_statistics = json.loads(squad_fpp_statistics.decode('utf-8')) if squad_fpp_statistics else None
    
    solo_statistics = redis_client.get('solo')
    solo_statistics = json.loads(solo_statistics.decode('utf-8')) if solo_statistics else None
    
    solo_fpp_statistics = redis_client.get('solo-fpp')
    solo_fpp_statistics = json.loads(solo_fpp_statistics.decode('utf-8')) if solo_fpp_statistics else None

    statistics = {
        "squad": squad_statistics,
        "squad-fpp": squad_fpp_statistics,
        "solo": solo_statistics,
        "solo-fpp": solo_fpp_statistics
    }

    if check_api_server() == 200:
        players_response = call_players_api_by_nickname(shard, nickname)
        if players_response.status_code == 200:
            account_id = get_account_id_from_players_api_response(players_response)
            ranked_stats_response = call_ranked_stats_api_by_account_id(shard, account_id)
            jsonified_ranked_stats_from_api = jsonify_ranked_stats_from_api(nickname, ranked_stats_response)
            send_to_users(jsonified_ranked_stats_from_api)
            
            response_body = {
                "account_id": account_id,
                "ranked_stats": jsonified_ranked_stats_from_api,
                "shard": get_shard_from_players_api_response(players_response),
                "matches": get_match_id_list_from_players_api_response(players_response),
                "statistics": statistics
            }
            response = {
                "is_pubgAPI_ok": 1,
                "body": response_body
            }
            return jsonify(response), 200
        else:
            response = {
                "error": "player does not exist."
            }
            return jsonify(response), 404
    else:
        print("PUBG API server error.")

        db_connection = mysql.connector.connect(
            host="de30-final-3-db-mysql.cve6gqgcih9t.ap-northeast-2.rds.amazonaws.com",
            user="admin",
            password="72767276",
            database="de30_final_3"
        )
        cursor = db_connection.cursor(dictionary=True)
        users_query = """
        SELECT *
        FROM users
        WHERE latest_nickname = %s
        ORDER BY latest_update DESC
        """
        cursor.execute(users_query, (nickname,))
        users_query_results = cursor.fetchall()

        account_ids = {row['account_id'] for row in users_query_results}
        if len(account_ids) == 1:
            account_id = users_query_results[0]['account_id']
            matches_query = """
            SELECT *
            FROM matches
            WHERE match_id IN (
                SELECT match_id
                FROM match_user
                WHERE account_id = %s
            )
            ORDER BY played_at DESC
            LIMIT 4;
            """
            cursor.execute(matches_query, (account_id,))
            matches_query_results = cursor.fetchall()

            match_user_results = []
            for match in matches_query_results:
                match_id = match['match_id']
                match_user_query = """
                SELECT *
                FROM match_user
                WHERE account_id = %s AND match_id = %s
                """
                cursor.execute(match_user_query, (account_id, match_id))
                match_user_results.extend(cursor.fetchall())

            response_body = {
                "account_id": account_id,
                "shard": shard,
                "users": users_query_results,
                "matches": matches_query_results,
                "match_user": match_user_results,
                "statistics": statistics
            }
            response = {
                "is_pubgAPI_ok": 0,
                "body": response_body
            }
            return jsonify(response), 200
        elif len(account_ids) == 0:
            response = {
                "error": "player does not exist."
            }
            return jsonify(response), 404
        else:
            response = {
                "error": "Nickname duplicated."
            }
            return jsonify(response), 400
