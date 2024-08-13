from app.services.JsonDataPreProcessorV1 import postRequestPreprocess
from app.services.JsonDataPreProcessorV1 import postRequestMLAim
from app.services.JsonDataPreProcessorV1 import postReqestMLSpeed
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

def post_request_preprocess(account_id, match_id, shard_id):
    try:
        logging.info(f"Preprocess request for account_id={account_id}, match_id={match_id}")
        
        total_radar_list = []
        total_landing_loc = []
        total_return_dict = {}
        
        PRT = postRequestPreprocess(account_id, match_id, shard_id)
        match_json = PRT.createMatchJsonData()
        matches_values, telemetryURL, mode, player_list = PRT.createMatchesjson(match_json)
        tele_json = PRT.createTelemetryData(telemetryURL)
        
        final_match_user_values = None

        logging.info(f"Number of players in match: {len(player_list)}")
        for player in player_list:
            match_user_values, matchUser_radar_data_list, landing_loc, match_id, map_id = PRT.createMatchUserJson(player, tele_json, match_json, mode)
            total_radar_list.append(matchUser_radar_data_list)
            total_landing_loc.append(landing_loc)
            if match_user_values['account_id'] == account_id:
                final_match_user_values = match_user_values

        if final_match_user_values is None:
            raise ValueError(f"No match found for account_id {account_id}")

        total_return_dict = {
            "match_id": match_id,
            "map_id": map_id,
            "players_data": total_landing_loc
        }

        final_data = PRT.avgAndStd(matches_values, total_radar_list)
        
        return final_data, final_match_user_values, total_return_dict
    except Exception as e:
        logging.error(f"Preprocessing failed: {e}")
        raise

def post_request_ml_shot(account_id, match_id, platform):
    PRM = postRequestMLAim(account_id,match_id, platform)
    match_json, tele_json, current_tier = PRM.create_rsj_and_match_and_telemetry()
    MLUser_record_value = PRM.createMLUserRecord(match_json,tele_json,account_id,match_id,current_tier)
    shot_record_value_list = PRM.produceShotRecord(tele_json,account_id,match_id)

    # print(MLUser_record_key)
    # print(MLUser_record_value)
    # print(shot_record_key)
    # print(shot_record_value_list)
    return MLUser_record_value, shot_record_value_list

def post_request_ml_speed(account_id, match_id, platform):
    PRM = postReqestMLSpeed(account_id, match_id, platform)
    process1 = PRM.makedictPerPlayer()
    process2, xy_location_list = PRM.makeListFromDict(process1)
    process3 = PRM.fill_vehicle_na(process2)
    process4 = PRM.throwParachute(process3)
    process5 = PRM.fill_walk(process4)
    speed_hack_value_record = PRM.dataPreProcessForML(process5)

    return speed_hack_value_record, xy_location_list


