from app.services.DataPreProcessorV2 import preprocessor
from app.services.apicollector import getApiToJson
from app.services.kafkaConnectorWithAvro import kafkaConnector
import requests
import logging

logger = logging.getLogger(__name__)

def main(kafka_broker, schema_registry_url, platform, playerName, api_key, current_season, matches_endpoint):
    print("###### PROCESS DEF : MODULEWORKERV2 MAIN ######")
    KC = kafkaConnector(kafka_broker, schema_registry_url)
    print("platform : " ,platform)
    print("playerName : " ,playerName)
    print("current_season : " ,current_season)
    print("matches_endpoint : " ,matches_endpoint)
    GA = getApiToJson(platform, playerName, api_key)
    accountId = GA.getPlayerId()
    PP = preprocessor(accountId, current_season, platform, playerName)
    matchId_list = GA.getMatchIdList()
    if accountId == None:
        print(f"No data with this account ID")
        pass

    if accountId.startswith("ai."):
        logger.info("AI player Detected.")
        pass

    else:
        recent_match_list = matchId_list[:]
        all_name_list = set()
        
        ranked_stats_endpoint = '/players/' + f'{accountId}' + '/seasons/' + f'{current_season}' + '/ranked'
        ranked_stats_json = GA.getOtherApiToJson(ranked_stats_endpoint)

        for index, i in enumerate(recent_match_list):
            print(index," : ",i)

        for match_id in recent_match_list:
            match_json = GA.getOtherApiToJson(matches_endpoint + match_id)
            matches_record_key, matches_record_value, tele_URL, mode, matchId = PP.createMatchesRecord(match_json)
            KC.produce_matches_message(matches_record_key, matches_record_value)

            tele_json = GA.getTelemtryJsonFromTelemetryURL(tele_URL)
            playerName_list = []
            for included_item in match_json['included']:
                try:
                    playerName_list.append(included_item['attributes']['stats']['name'])
                    all_name_list.add(included_item['attributes']['stats']['name'])
                except KeyError as e:
                    continue
                    print(f"matches api 에서 이름 추출중 키 에러 발생 : {e}")
                except Exception as e:
                    continue
                    print(f"matches api 에서 이름 추출중 예외 에러 발생 : {e}")

            print(playerName_list)
            
            for player in playerName_list:
                print("player : ", player)
                GA.playerName = player
                GA.id_response = requests.get(GA.id_search_by_nickname_url + GA.playerName, headers=GA.apis_header)
                
                try:
                    accountId = GA.getPlayerId()
                    if accountId != None:
                        if accountId.startswith("ai."):
                            logger.info("AI player Detected.")
                            continue
                        else:
                            PP = preprocessor(accountId, current_season, platform, player)
                            
                            ranked_stats_endpoint = '/players/' + f'{accountId}' + '/seasons/' + f'{current_season}' + '/ranked'
                            ranked_stats_json = GA.getOtherApiToJson(ranked_stats_endpoint)
                            
                            current_tier = PP.createAndProduceUsersRecord(ranked_stats_json,KC)
                            matchUser_record_key, matchUser_record_value, total_shot = PP.createMatchUserRecord(tele_json,match_json, mode, matchId, accountId)
                            KC.produce_matchUser_message(matchUser_record_key, matchUser_record_value)

                            MLUser_record_key, MLUser_record_value = PP.createMLUserRecord(tele_json,accountId,matchId,current_tier,total_shot)
                            KC.produce_mlUser_message(MLUser_record_key, MLUser_record_value)
                            
                            PP.produceShotRecord(tele_json,KC,accountId,matchId)
                    else:
                        print(f"no data in {accountId}")
                except KeyError as e:
                    continue
                    print(f"playerName_list에서 로직 순환중 키 에러 발생 : {e}")
                except Exception as e:
                    continue
                    print(f"playerName_list에서 로직 순환중 예외 에러 발생 : {e}")
        
