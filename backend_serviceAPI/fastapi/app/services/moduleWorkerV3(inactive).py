from app.services.DataPreProcessorV2 import preprocessor
from app.services.apicollector import getApiToJson
from app.services.kafkaConnectorWithAvro import kafkaConnector

# from DataPreProcessorV2 import preprocessor
# from apicollector import getApiToJson
# from kafkaConnectorWithAvro import kafkaConnector

import requests
import random

def main(kafka_broker, schema_registry_url, platform, playerName, api_key, current_season, matches_endpoint):
    # current_season = 'division.bro.official.pc-2018-30'
    playerName_set = set()
    print("platform : " ,platform)
    print("playerName : " ,playerName)
    print("current_season : " ,current_season)
    print("matches_endpoint : " ,matches_endpoint)
    # global playerName_set
    KC = kafkaConnector(kafka_broker, schema_registry_url)
    GA = getApiToJson(platform, playerName, api_key)
    accountId = GA.getPlayerId()
    if accountId is None:
        print("Failed to get account ID, exiting.")
        return
    matchId_list = GA.getMatchIdList()

    for match_id in matchId_list:
        match_json = GA.getOtherApiToJson(matches_endpoint + match_id)
        if match_json['data']['attributes']['matchType'] == "competitive":
            print(f"{match_json['data']['attributes']['matchType']} is Competitve. Processing...")
            for included_item in match_json['included']:
                try:
                    playerName_set.add(included_item['attributes']['stats']['name'])
                except KeyError as e:
                    continue
                    print(f"WARNING : KeyError during name extraction: {e}")
                except Exception as e:
                    continue
                    print(f"WARNING : Exception during name extraction: {e}")

            print(f"{len(playerName_set)} names collected.")
        else :
            print(f"{match_json['data']['attributes']['matchType']} Not Competitive. Skipping...")
            continue
        
    while playerName_set:
        print("@@@@@@ LOOP ENTER WHILE PLAYERNAME_SET @@@@@")
        player = random.choice(list(playerName_set))
        playerName_set.remove(player)
        print("player : ", player)

        try:
            accountId = GA2.getPlayerId()
            if accountId.startswith('ai.'):
                print("AI player detected. Skipping...")
                continue
            if accountId:
                print("@@@@@ CHECK INSTANCES BEFORE CREATE NEW CLASS @@@@@")
                print(f"platform : {platform}")
                print(f"current_season : {current_season}")
                print(f"api_key : {api_key[:10]}")
                print(f"player : {player}")
                print(f"accountId : {accountId}")
                GA2 = getApiToJson(platform, player, api_key)
                matchId_list = GA2.getMatchIdList()
                PP = preprocessor(accountId, current_season, platform, player)
                ranked_stats_endpoint = '/players/' + f'{accountId}' + '/seasons/' + f'{current_season}' + '/ranked'
                ranked_stats_json = GA2.getOtherApiToJson(ranked_stats_endpoint)
                PP.createAndProduceUsersRecord(ranked_stats_json,KC)

                for match_id in matchId_list:
                    match_json = GA2.getOtherApiToJson(matches_endpoint + match_id)
                    if match_json['data']['attributes']['matchType'] == "competitive":
                        print(f"{match_json['data']['attributes']['matchType']} is Competitve. Processing...")
                        single_match_players = []
                        for included_item in match_json['included']:
                            try:
                                # print("#### extract player name ####", included_item['attributes']['stats']['name'])
                                playerName_set.add(included_item['attributes']['stats']['name'])
                                print("insert into player_name_set")
                                if included_item['attributes']['stats']['name'] not in single_match_players:
                                    single_match_players.append(included_item['attributes']['stats']['name'])
                                    print("insert into single_match_player_list")
                            except KeyError as e:
                                continue
                                print(f"KeyError during name extraction: {e}")
                            except Exception as e:
                                continue
                                print(f"Exception during name extraction: {e}")
                        matches_record_key, matches_record_value, tele_URL, mode, matchId = PP.createMatchesRecord(match_json)
                        tele_json = GA2.getTelemtryJsonFromTelemetryURL(tele_URL)

                    # for_produce_matchUser_record_list = []
                    # for_matches_update_value_list = []

                    # PP.createAndProduceUsersRecord(ranked_stats_json, KC)
                    # print(single_match_players)
                    # for i in single_match_players:
                    #     matchUser_record_key, matchUser_record_value, for_matches_update_value = PP.createMatchUserRecord(tele_json, match_json, mode, matchId, i)
                    #     for_matches_update_value_list.append(for_matches_update_value)
                    #     for_produce_matchUser_record_list.append([matchUser_record_key, matchUser_record_value])
                    # print("통합완료")
                    # matches_record_value_ap = PP.avgAndStd(matches_record_value, for_matches_update_value_list)
                    # print("matches 업데이트중")
                    # KC.produce_matches_message(matches_record_key, matches_record_value_ap)
                    # for i in range(len(for_produce_matchUser_record_list)):
                    #     print(for_produce_matchUser_record_list[i][0])
                    #     print(for_produce_matchUser_record_list[i][1])
                    #     KC.produce_matchUser_message(for_produce_matchUser_record_list[i][0], for_produce_matchUser_record_list[i][1])
                    #     ("match_user 데이터 전달중")



                # PP.createMLUserRecord(tele_json)
                # PP.produceShotRecord(tele_json, KC)
            else:
                print("No data in this accountId. Skipping...")
                continue
        except KeyError as e:
            continue
            print(f"KeyError during playerName_list processing: {e}")
        except Exception as e:
            continue
            print(f"Exception during playerName_list processing: {e}")

# kafka_broker='10.11.10.58:9092'
# schema_registry_url='http://10.11.10.58:8081'
# platform= 'steam'
# playerName='Xiao_Sxxng'
# api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIwOTczZWUxMC0wOTZlLTAxM2QtY2NlNi0zMmFkODc5M2Q4OGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzE4MDM0MTc4LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImhlaGViYWxzc2EifQ.ADpdC0UInjTkDeVJXNjtZvMf4rNQAyrzQqWuPGvuteE'
# current_season='division.bro.official.pc-2018-30'
# matches_endpoint='/matches/'

# main(kafka_broker, schema_registry_url, platform, playerName, api_key, current_season, matches_endpoint)