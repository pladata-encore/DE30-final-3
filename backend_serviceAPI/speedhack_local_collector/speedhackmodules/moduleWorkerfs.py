from apicollectorfs import getApiToJson
from DataLoaderfs import pyMysqlConnector
from preprocessorForSpeedHack import datapreProcessorForML
from playerNames import player_nicknames

def main(platform,api_key,current_season,matches_endpoint,players_endpoint,host,database,user,password,speedhack_table_ap):
    PMC = pyMysqlConnector(host, database, user, password)
    for p in player_nicknames:
        GA = getApiToJson(platform, p, api_key)
        try:
            account_id = GA.getPlayerId()
            matchId_list = GA.getMatchIdList()
        except:
            pass

        try:
            for m in matchId_list:
                match_endpoint = matches_endpoint + m
                # print("matches_endpoint : ", match_endpoint)
                matches_json = GA.getOtherApiToJson(match_endpoint,platform)
                if matches_json['data']['attributes']['matchType'] == 'competitive':
                    # print(matches_json['data']['attributes']['matchType'])
                    match_player_name_list = []
                    tele_json = GA.getTelemetryJsonFromMatchId(m)
                    for pp in tele_json:
                        try:
                            if [pp['character']['name'],pp['character']['accountId']] not in match_player_name_list and pp['character']['name'] != 'Bear':
                                match_player_name_list.append([pp['character']['name'],pp['character']['accountId']])
                        except:
                            pass
                    for pn in match_player_name_list:
                        PP = datapreProcessorForML(pn[0])
                        process1 = PP.makedictPerPlayer(tele_json)
                        process2 = PP.makeListFromDict(process1)
                        process3 = PP.fill_vehicle_na(process2)
                        process4 = PP.throwParachute(process3)
                        process5 = PP.fill_walk(process4)
                        process6 = PP.dataPreProcessForML(process5,tele_json,m)
                        process7 = [i for i in process6 if i[-4]< 11]
                        print("final process : ", len(process7))
                        for i in process7:
                            if i[-1] >= 100:
                                print(i)
                        updated_process7 = [
                            (
                                item[0],  # match_id
                                pn[0],  # account_name (update)
                                pn[1],  # account_id (update)
                                item[3],  # vehicle_id
                                item[4],  # event_time_1
                                item[5],    # event_time_2
                                item[6],    # x1
                                item[7],    # x2
                                item[8],    # y1
                                item[9],    # y2   
                                item[10],   # z1
                                item[11],   # z2
                                item[12],   # distance
                                item[13],   # time_diff
                                item[14],   # event_log
                                item[15],   # cm_per_s
                                item[16]    # km_per_h
                            )
                            for item in process7 if item[13] > 0.5
                        ]
                        print(pn)   

                        PMC.getColumnNames(speedhack_table_ap)
                        PMC.insertDataToMysql(speedhack_table_ap,updated_process7)
                else:
                    # print("Not Competitive. Skip...")
                    continue
        except:
            pass



