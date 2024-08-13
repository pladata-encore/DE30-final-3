from datetime import datetime
import time
import numpy as np
import json
import requests

class postRequestPreprocess:
    def __init__(self, accountId, match_id, shard_id):
        self.accountId = accountId
        self.match_id = match_id
        self.telemetry_url = None
        self.apikey = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIwOTczZWUxMC0wOTZlLTAxM2QtY2NlNi0zMmFkODc5M2Q4OGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzE4MDM0MTc4LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImhlaGViYWxzc2EifQ.ADpdC0UInjTkDeVJXNjtZvMf4rNQAyrzQqWuPGvuteE'
        self.season_id = "division.bro.official.pc-2018-31"
        self.map_id = None
        self.shard_id = shard_id
        
    def createMatchJsonData(self):
            apis_header = {
                "Authorization": f"Bearer {self.apikey}",
                "Accept": "application/vnd.api+json"
            }
            matches_url = f"https://api.pubg.com/shards/{self.shard_id}/matches/{self.match_id}"
            print(matches_url)
            
            try:
                match_json = requests.get(matches_url, headers=apis_header)
                match_json.raise_for_status()
                return match_json.json()
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                print(f"Failed with shard_id {self.shard_id} : {e}")
    
    def createMatchesjson(self,json_data):
        print("############################## process def : createMatchesJson ##############################")
        self.matchId = json_data['data']['id']
        key_wave = json_data['data']['attributes']
        self.mode = key_wave['gameMode']
        self.shard = key_wave['shardId']
        map = key_wave['mapName']
        played_at = datetime.strptime(key_wave['createdAt'],"%Y-%m-%dT%H:%M:%SZ")
        # played_at_millis = int(time.mktime(played_at.timetuple()) * 1000)
        duration = int(key_wave['duration'])
        for include in json_data['included']:
            if include['type'] == 'asset':
                telemetryURL = include['attributes']['URL']
                break

        player_list = []
        for i in json_data['included']:
            try:
                if i['attributes']['stats']['playerId'] not in player_list:
                    player_list.append(i['attributes']['stats']['playerId'])
            except:
                pass

        matches_record_value = {
            "match_id" :        self.matchId,
            "mode_id" :         self.mode,
            "season_id" :       self.season_id,
            "shard" :           self.shard_id,
            "map_id" :          map,
            "duration" :        duration,
            "played_at" :       str(played_at),
            "telemetry_url" :   telemetryURL,
            "belligerence_avg": None,
            "belligerence_std": None,
            "combat_avg" :      None ,
            "combat_std" :      None ,
            "viability_avg":    None ,
            "viability_std":    None ,
            "utility_avg" :     None ,
            "utility_std" :     None ,
            "sniping_avg" :     None ,
            "sniping_std" :     None
                }
        # for key, value in matches_record_value.items():
        #     print(f"{key}: {value}")

        return matches_record_value, telemetryURL, self.mode, player_list

    def createTelemetryData(self,telemetryURL):
        telemetry_header = {
            "Accept": "application/vnd.api+json",
            "Accept-Encoding": "gzip"
        }
        print("telemetryURL : ", telemetryURL)
        try:
            telemetry_response = requests.get(telemetryURL, headers=telemetry_header)
            
            # 응답 상태 코드 확인
            if telemetry_response.status_code != 200:
                print(f"Error: Received status code {telemetry_response.status_code}")
                return None
            
            # 응답 내용 출력 (디버깅용)
            # print("Response content:", telemetry_response.content[:500])  # 처음 500자를 출력
            
            # JSON 응답 파싱
            return telemetry_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            return None
        
    def createMatchUserJson(self, account_id, telemetry_data, match_json_data, mode):
        print("############################## process def : createMatchUserJson ##############################")
        self.mode = mode
        self.total_shots = 0
        kill_distance_list = []
        hit_count = 0
        landed_zone_x = 0
        landed_zone_y = 0
        throw_count = 0
        vehicle_count = 0
        hitByVehicle_damage = 0
        self.kills = 0
        self.assists = 0
        ranking = 0
        revives = 0
        heals = 0
        survival_time = 0
        self.damageDealt = 0
        self.dBNOs = 0
        boost_count = 0
        rideDistance = 0
        swimDistance = 0
        walkDistance = 0
        total_distance = 0
        self.landing_loc = {}

        for i in telemetry_data:
            try:
                if i['_T'] == "LogPlayerAttack" and i['attacker']['accountId'] == account_id and i['common']['isGame'] >= 0.1 and i['attackId'] >= 10000:
                    self.total_shots+=1
                if i['_T'] == 'LogPlayerTakeDamage' and i['damageTypeCategory'] == "Damage_Gun" and i['attacker']['accountId'] == account_id:
                    hit_count += 1 
                if i['_T'] == 'LogPlayerTakeDamage' and i['damageTypeCategory'] == 'Damage_VehicleHit' and i['attacker']['accountId'] == account_id:
                    hitByVehicle_damage+=i['damage']
                elif i['_T'] == 'LogPlayerKillV2' and i['killer']['accountId'] == account_id:
                    kill_distance_list.append(i['killerDamageInfo']['distance'])
                elif i['_T'] == 'LogParachuteLanding' and i['character']['accountId'] == account_id and 0.1 <= i['common']['isGame'] <= 0.5:
                    landed_zone_x = i['character']['location']['x']
                    landed_zone_y = i['character']['location']['y']
                elif i['_T'] == 'LogPlayerUseThrowable' and i['attacker']['accountId'] == account_id:
                    throw_count+=1
                elif i['_T'] == ('LogVehicleRide' or i['_T'] == 'LogVehicleLeave') and i['character']['accountId'] == account_id and i['vehicle']['vehicleType'] != 'TransportAircraft':
                    vehicle_count+=1
            except KeyError as e:
                continue
                print(f"KeyError in for i in telemetry_data : {e}")
            except Exception as e:
                continue
                print(f"ExceptionError for i in telemetry_data : {e}")
        if len(kill_distance_list) == 0:
            avg_kill_distance = 0
            longest_kill_dist = 0
        else:
            avg_kill_distance = (sum(kill_distance_list)/len(kill_distance_list))/100
            longest_kill_dist = max(kill_distance_list)/100
        if self.total_shots == 0:
            self.accuracy = 0
        else:
            self.accuracy = (hit_count/self.total_shots)*100

        for i in match_json_data['included']:
            try:
                key_wave = i['attributes']['stats']
                if key_wave['playerId'] == account_id:
                    self.kills = key_wave['kills']
                    self.assists = key_wave['assists']
                    ranking = int(key_wave['winPlace'])
                    revives = key_wave['revives']
                    heals = key_wave['heals']
                    survival_time = int(key_wave['timeSurvived'])
                    self.damageDealt = key_wave['damageDealt']
                    self.dBNOs = key_wave['DBNOs']
                    boost_count = key_wave['boosts']
                    rideDistance = key_wave['rideDistance']
                    swimDistance = key_wave['swimDistance']
                    walkDistance = key_wave['walkDistance']
                    total_distance = (rideDistance + swimDistance + walkDistance)/1000
            except KeyError as e:
                continue
                print(f"KeyError for i in match_json_data['included'] : {e}")
            except Exception as e:
                continue
                print(f"ExceptionError for i in match_json_data['included'] : {e}")

        belligerence = None
        combat = self.accuracy*10 + self.kills*50 + self.dBNOs + self.assists*30 + longest_kill_dist
        viability = survival_time + heals*30 + boost_count*30
        utility = throw_count*10 + vehicle_count*0.5 + hitByVehicle_damage*0.5
        sniping = avg_kill_distance
        
        for i in telemetry_data:
            try:
                if i['_T'] == "LogMatchStart":
                    self.map_name = i['mapName']
            except:
                pass
        # print(account_id)
        for i in telemetry_data:
            try:
                if i['character']['accountId'] == account_id:
                    if i['_T'] == "LogParachuteLanding":
                        # self.landing_loc = [self.matchId,self.map_name,account_id,self.total_shots,i['character']['location']['x'],i['character']['location']['y']]
                        # print(self.landing_loc)
                        self.landing_loc = {
                                "account_id":           account_id,
                                "total_shots":          self.total_shots,
                                "landing_coordinates_x": float(i['character']['location']['x']),
                                "landing_coordinates_y": float(i['character']['location']['y'])
                        }
                        break
            except KeyError as e:
                continue
                print(f"KeyError for i in match_json_data['included'] : {e}")
            except Exception as e:
                continue
                print(f"ExceptionError for i in match_json_data['included'] : {e}")

        print("account_id : ",  account_id)
        print("season_id : ",   self.season_id)
        print("match_id : ",    self.matchId)
        print("mode_id : ",     self.mode)
        print("shard : ",       self.shard_id)
        print("total_shots :",  self.total_shots)
        print("total_distance :", total_distance)
        print("kills :",        self.kills)
        print("assists :",      self.assists)
        print("ranking :",      ranking)
        print("revives :",      revives)
        print("longest_kill_dist :", longest_kill_dist)
        print("accuracy :",     self.accuracy)
        print("heal_count :",   heals)
        print("lifetime :",     survival_time)
        print("landed_location_x :",landed_zone_x)
        print("landed_location_y :",landed_zone_y)
        print("avg_kill_distance :",avg_kill_distance)
        print("damage_dealt :" ,self.damageDealt)
        print("knockdowns :",   self.dBNOs)
        print("boost_count :",  boost_count)
        print("throw_count :",          throw_count)
        print("vehicle_use_count:" ,    vehicle_count)
        print("damage_from_vehicle :",  hitByVehicle_damage)

        matchUser_record_value = {
            "account_id":       account_id,
            "season_id" :       self.season_id,
            "match_id" :        self.matchId,
            "mode_id" :         self.mode,
            "shard" :           self.shard,
            "total_shots":      self.total_shots,
            "total_distance":   total_distance,
            "kills":            self.kills,
            "assists":          self.assists,
            "ranking":          ranking,
            "revives":          revives,
            "longest_kill_dist":longest_kill_dist,
            "accuracy":         self.accuracy,
            "heal_count":       heals,
            "lifetime":         survival_time,
            "landed_location_x":landed_zone_x,
            "landed_location_y":landed_zone_y,
            "avg_kill_distance":avg_kill_distance,
            "damage_dealt":     self.damageDealt,
            "knockdowns":       self.dBNOs,
            "boost_count":      boost_count,
            "throw_count":      throw_count,
            "vehicle_use_count" : vehicle_count,
            "damage_from_vehicle" : hitByVehicle_damage,
            "belligerence" :    belligerence,
            "combat" :          combat,
            "viability" :       viability,
            "utility" :         utility,
            "sniping" :         sniping
                }
        matchUser_radar_data_list = [combat,viability,utility,sniping]

        return matchUser_record_value, matchUser_radar_data_list, self.landing_loc ,self.match_id, self.map_name
        
    def avgAndStd(self,target, data):
        print("############################## process def : avgAndStd ##############################")
        array = np.array(data)

        means = np.mean(array, axis=0)
        std_devs = np.std(array, axis=0)

        target["combat_avg"] = means[0]
        target["combat_std"] = std_devs[0]
        target["viability_avg"] = means[1]
        target["viability_std"] = std_devs[1]
        target["utility_avg"] = means[2]
        target["utility_std"] = std_devs[2]
        target["sniping_avg"] = means[3]
        target["sniping_std"] = std_devs[3]

        return target

class postRequestMLAim:
    def __init__(self, accountId, match_id, shard_id):
        self.accountId = accountId
        self.match_id = match_id
        self.telemetry_url = None
        self.apikey = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIwOTczZWUxMC0wOTZlLTAxM2QtY2NlNi0zMmFkODc5M2Q4OGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzE4MDM0MTc4LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImhlaGViYWxzc2EifQ.ADpdC0UInjTkDeVJXNjtZvMf4rNQAyrzQqWuPGvuteE'
        self.season_id = "division.bro.official.pc-2018-31"
        self.shard_id = shard_id
        self.apis_header = {
            "Authorization": f"Bearer {self.apikey}",
            "Accept": "application/vnd.api+json"
        }
        self.telemetry_header = {
            "Accept": "application/vnd.api+json",
            "Accept-Encoding": "gzip"
                }

    def create_rsj_and_match_and_telemetry(self):
        print("######################### process def : create_rsj_and_match_and_telemetry ################################")
        ranked_stats_endpoint = "https://api.pubg.com/shards/"+self.shard_id+'/players/' + self.accountId + '/seasons/' + self.season_id + '/ranked'
        print(ranked_stats_endpoint)

        ranked_stats = requests.get(ranked_stats_endpoint, headers=self.apis_header)
        ranked_stats.raise_for_status()

        if ranked_stats.status_code == 200:
            ranked_stats_json = ranked_stats.json()
            # print(ranked_stats_json)
        else:
            print("fail to get ranked_stats_json")

        key_wave = ranked_stats_json['data']['attributes']['rankedGameModeStats']
        mode_list = list(key_wave.keys()) 
        current_tier=""
        current_tier_list = []
        for i in mode_list:
            current_tier_list.append(key_wave[i]['currentTier']['tier'])
        if "Master" in current_tier_list:
            current_tier = "Master"
        elif "Diamond" in current_tier_list:
            current_tier = "Diamond"
        elif "Platinum" in current_tier_list:
            current_tier = "Platinum"
        elif "Gold" in current_tier_list:
            current_tier = "Gold"
        elif "Silver" in current_tier_list:
            current_tier = "Silver"
        else:
            current_tier = "Bronze"

        print(current_tier)
        matches_url = f"https://api.pubg.com/shards/{self.shard_id}/matches/{self.match_id}"
        print(matches_url)
        match_data = requests.get(matches_url, headers=self.apis_header)
        match_data.raise_for_status()

        if match_data.status_code == 200:
            match_json = match_data.json()
            for i in match_json['included']:
                if "attributes" in i:
                    a = i.get("attributes",{})
                    if "URL" in a:
                        b = a.get("URL","")
            
            print(b)
            telemetry_response = requests.get(b, headers=self.telemetry_header)
            if telemetry_response.status_code ==200:
                return match_json, telemetry_response.json(), current_tier
            else:
                print("fail to get telemetry response")

    def createMLUserRecord(self,match_json,tele_json_data,accountId,matchId,currentTier_tier):
        print("######################### process def : createMLUserRecord ################################")
        total_shots = 0
        hit_count = 0
        head_count = 0
        for i in match_json['included']:
            try:
                if 'attributes' in i:
                    a = i.get("attributes",{})
                    if 'stats' in a:
                        b = a.get('stats',{})
                        if b['playerId'] == accountId:
                            kills = b['kills']
                            DBNOs = b['DBNOs']
                            assists = b['assists']
                            total_damage = b['damageDealt']
                            break
            except KeyError as e:
                print(e)
                continue
            except Exception as e:
                print(e)
                continue
        for i in tele_json_data:
            try:
                if i['_T'] == "LogPlayerAttack" and i['attacker']['accountId'] == accountId and i['common']['isGame'] >= 0.1 and i['attackId'] >= 10000:
                    total_shots += 1
                if i['_T'] == 'LogPlayerTakeDamage' and i['damageTypeCategory'] == "Damage_Gun" and i['attacker']['accountId'] == accountId:
                    hit_count += 1 
                    if i['damageReason'] == "HeadShot":
                        head_count+=1
                # if i['_T'] == 'LogPlayerTakeDamage' and i['damageTypeCategory'] == "Damage_Gun" and i['attacker']['accountId'] == accountId and i['damageReason'] == "HeadShot":
                #     head_count+=1
            except KeyError as e:
                print(f"KeyError: {e}")
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

        # MLUser_record_key = {"account_id": accountId, "match_id" : matchId}
        MLUser_record_value = {
            "account_id": accountId,
            "match_id" : matchId,
            "current_tier" : currentTier_tier,
            "kills" : kills,
            "knockdowns" : DBNOs,
            "assists" : assists,
            "total_damage" : total_damage,
            "total_shot" : int(total_shots),
            "hit_count" : int(hit_count),
            "head_shot" : int(head_count)
                }

        return MLUser_record_value

    def produceShotRecord(self,tele_data,accountId,matchId):
        print("######################### process def : produceShotRecord ################################")
        self.is_hit = False
        self.hit_point = None
        self.hit_distance = None
        attack_id = 0
        weapon_id = ""
        timeStamp = ""
        shot_record_value_list=[]
        
        for i in tele_data:
            try:
                if i['attacker']['accountId'] == accountId and i['common']['isGame'] >= 0.1 and i['weapon']['subCategory'] == "Main" and  i['_T'] == "LogPlayerAttack":
                    attack_id = int(i['attackId'])
                    weapon_id = str(i['weapon']['itemId'])
                    timeStamp = datetime.strptime(i['_D'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    timeStamp = timeStamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    # print(timeStamp)
                    for j in tele_data:
                        if j['_T'] == "LogPlayerTakeDamage" and j['attackId'] == attack_id:
                            self.is_hit = True
                            self.hit_point = j['damageReason']
                            self.hit_distance = ((j['attacker']['location']['x']-j['victim']['location']['x'])**2 + (j['attacker']['location']['y']-j['victim']['location']['y'])**2 + (j['attacker']['location']['z']-j['victim']['location']['z'])**2)**(1/2)
                            break
                    # shot_record_key = {"match_id" : matchId, "attack_id" : attack_id}
                    shot_record_value = {
                        "account_id": accountId,
                        "match_id" : matchId,
                        "attack_id" : attack_id,
                        "weapon_id" : weapon_id,
                        "is_hit" : self.is_hit,
                        "hit_point" : self.hit_point,
                        "hit_distance" : self.hit_distance,
                        "timeStamp" : timeStamp
                            }
                    # print(shot_record_value)
                    shot_record_value_list.append(shot_record_value)
                    self.is_hit = False
                    self.hit_point = None
                    self.hit_distance = None
            except KeyError as e:
                continue
                print("key Error :",e)
            except Exception as e:
                continue
                print("Exception Error :",e)
        return shot_record_value_list

class postReqestMLSpeed:
    def __init__(self,account_id, match_id, platform):
        self.account_id = account_id
        self.match_id = match_id
        self.shard_id = platform
        self.apikey = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIwOTczZWUxMC0wOTZlLTAxM2QtY2NlNi0zMmFkODc5M2Q4OGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzE4MDM0MTc4LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImhlaGViYWxzc2EifQ.ADpdC0UInjTkDeVJXNjtZvMf4rNQAyrzQqWuPGvuteE'
        self.season_id = "division.bro.official.pc-2018-31"

        self.apis_header = {
            "Authorization": f"Bearer {self.apikey}",
            "Accept": "application/vnd.api+json"
        }
        self.telemetry_header = {
            "Accept": "application/vnd.api+json",
            "Accept-Encoding": "gzip"
                }

        matches_url = f"https://api.pubg.com/shards/{self.shard_id}/matches/{self.match_id}"
        # print(matches_url)
        match_data = requests.get(matches_url, headers=self.apis_header)
        match_data.raise_for_status()

        if match_data.status_code == 200:
            self.match_json = match_data.json()
            for i in self.match_json['included']:
                if "attributes" in i:
                    a = i.get("attributes",{})
                    if "URL" in a:
                        b = a.get("URL","")
            
            # print(b)
            telemetry_response = requests.get(b, headers=self.telemetry_header)
            if telemetry_response.status_code ==200:
                self.tele_json = telemetry_response.json()
            else:
                print("fail to get telemetry response")

    def makedictPerPlayer(self):
        player_dict = []
        for i in self.tele_json:
            try:
                if i['character']['accountId'] == self.account_id: 
                    player_dict.append(i)

            except:
                pass
        for i in self.tele_json:
            try:
                if i['attacker']['accountId'] == self.account_id:
                    player_dict.append(i)
            except:
                pass
        print("number of logs : ", len(player_dict))
        # for i in player_dict:
        #     print(i)
        return player_dict

    def makeListFromDict(self,player_dict):
        player_list = []
        for i in player_dict:
            try:
                if i['common']['isGame'] > 0.5:
                    if 'vehicle' in i.keys():
                        if i['vehicle'] is not None:
                            if 'character' in i.keys():
                                if i['character']['accountId'] == self.account_id:
                                    if i['character']['location']['x']>0 and i['character']['location']['y']>0 and i['character']['location']['z']>0:
                                        player_list.append([i['character']['name'],\
                                                    i['character']['accountId'],\
                                                    i['character']['location']['x'],\
                                                    i['character']['location']['y'],\
                                                    i['character']['location']['z'],\
                                                    i['character']['isInVehicle'],\
                                                    i['vehicle']['vehicleId'],\
                                                    i['_D'],\
                                                    i['_T']
                                                        ])
                            else:
                                if i['attacker']['accountId'] == self.account_id:
                                    if i['attacker']['location']['x']>0 and i['attacker']['location']['y']>0 and i['attacker']['location']['z']>0:
                                        player_list.append([i['attacker']['name'],\
                                                    i['attacker']['accountId'],\
                                                    i['attacker']['location']['x'],\
                                                    i['attacker']['location']['y'],\
                                                    i['attacker']['location']['z'],\
                                                    i['attacker']['isInVehicle'],\
                                                    i['vehicle']['vehicleId'],\
                                                    i['_D'],\
                                                    i['_T']
                                                        ])
                        else:
                            if 'character' in i.keys():
                                if i['character']['accountId'] == self.account_id:
                                    if i['character']['location']['x']>0 and i['character']['location']['y']>0 and i['character']['location']['z']>0:
                                        player_list.append([i['character']['name'],\
                                                    i['character']['accountId'],\
                                                    i['character']['location']['x'],\
                                                    i['character']['location']['y'],\
                                                    i['character']['location']['z'],\
                                                    i['character']['isInVehicle'],\
                                                    None,\
                                                    i['_D'],\
                                                    i['_T']
                                                        ])
                            else:
                                if i['attacker']['accountId'] == self.account_id:
                                    if i['attacker']['location']['x']>0 and i['attacker']['location']['y']>0 and i['attacker']['location']['z']>0:
                                        player_list.append([i['attacker']['name'],\
                                                    i['attacker']['accountId'],\
                                                    i['attacker']['location']['x'],\
                                                    i['attacker']['location']['y'],\
                                                    i['attacker']['location']['z'],\
                                                    i['attacker']['isInVehicle'],\
                                                    None,\
                                                    i['_D'],\
                                                    i['_T']
                                                        ])
                    else:
                            if 'character' in i.keys():
                                if i['character']['accountId'] == self.account_id:
                                    if i['character']['location']['x']>0 and i['character']['location']['y']>0 and i['character']['location']['z']>0:
                                        player_list.append([i['character']['name'],\
                                                    i['character']['accountId'],\
                                                    i['character']['location']['x'],\
                                                    i['character']['location']['y'],\
                                                    i['character']['location']['z'],\
                                                    i['character']['isInVehicle'],\
                                                    None,\
                                                    i['_D'],\
                                                    i['_T']
                                                        ])
                            else:
                                if i['attacker']['accountId'] == self.account_id:
                                    if i['attacker']['location']['x']>0 and i['attacker']['location']['y']>0 and i['attacker']['location']['z']>0:
                                        player_list.append([i['attacker']['name'],\
                                                    i['attacker']['accountId'],\
                                                    i['attacker']['location']['x'],\
                                                    i['attacker']['location']['y'],\
                                                    i['attacker']['location']['z'],\
                                                    i['attacker']['isInVehicle'],\
                                                    None,\
                                                    i['_D'],\
                                                    i['_T']
                                                        ])
            except KeyError as e:
                # print(e)
                pass
        print("number of Processed list : ",len(player_list))
        # for i in player_list:
        #     print(i)
        xy_location_list = []
        print(len(player_dict[1:]))
        for i in player_dict[1:]:
            try:
                if 'character' in i and i['common']['isGame'] > 0.5:
                    xy_location_list.append({
                                            "location_x" : i['character']['location']['x'],
                                            "location_y" : i['character']['location']['y']
                                             })
                elif 'attacker' in i and i['common']['isGame'] > 0.5:
                    xy_location_list.append({
                                            "location_x" : i['attacker']['location']['x'],
                                            "location_y" : i['attacker']['location']['y']
                                             })                    
            except:
                pass
        print(len(xy_location_list))
        # print(xy_location_list)

        return player_list, xy_location_list

    def fill_vehicle_na(self,player_list):
        current_vehicle = None
        result = []

        for entry in player_list:
            # 4번째 인덱스가 None이 아니고 마지막 인덱스가 LogVehicleRide일 때
            if entry[6] is not None and entry[-1] == 'LogVehicleRide':
                current_vehicle = entry[6]
            
            # 현재 차량이 지정된 상태라면 4번째 인덱스를 현재 차량으로 설정
            if current_vehicle is not None:
                entry[6] = current_vehicle
            
            if current_vehicle == "BP_EmergencyPickupVehicle_C":
                if entry[-1] == 'LogParachuteLanding':
                    current_vehicle = None

            elif current_vehicle == "DummyTransportAircraft_C":
                if entry[-1] == 'LogParachuteLanding':
                    current_vehicle = None
            else:
            # LogVehicleLeave를 만나면 current_vehicle을 None으로 설정
                if entry[-1] == 'LogVehicleLeave':
                    current_vehicle = None
                
            result.append(entry)
        print("fill Noned vehicle : ",len(result))
        # for i in result:
        #     print(i)
        return result

    def throwParachute(self,player_list):
        for i in range(len(player_list)):
            if player_list[i][8] == "LogParachuteLanding":
                player_list = player_list[i+1:]
                break
        print("throw first parachute :",len(player_list))
        # for i in player_list:
        #     print(i)
        return player_list

    def fill_walk(self,player_list):
        for i in player_list:
            if i[6] == None:
                i[6] = "walk"
        print("fill_walk :",len(player_list))
        # for entry in player_list:
        #     print(entry)
        return player_list

    def dataPreProcessForML(self,list):
        mapping = [
            ('AirBoat_V2_C',        'Airboat'),
            ('AquaRail_A_01_C',     'Aquarail'),
            ('AquaRail_A_02_C',     'Aquarail'),
            ('AquaRail_A_03_C',     'Aquarail'),
            ('AquaRail_C',          'AquaRail'),
            ('BP_ATV_C',            'Quad'),
            ('BP_BRDM_C',           'BRDM-2'),
            ('BP_Bicycle_C',        'Mountain Bike'),
            ('BP_Blanc_C',          'Coupe SUV'),
            ('BP_Blanc_Esports_C',  'Coupe SUV'),
            ('BP_CoupeRB_C',        'Coupe RB'),
            ('BP_Dirtbike_C',       'Dirt Bike'),
            ('BP_Food_Truck_C',     'Food Truck'),
            ('BP_KillTruck_C',      'Kill Truck'),
            ('BP_LootTruck_C',      'Loot Truck'),
            ('BP_M_Rony_A_01_C',    'Rony'),
            ('BP_M_Rony_A_02_C',    'Rony'),
            ('BP_M_Rony_A_03_C',    'Rony'),
            
            ('BP_McLarenGT_Lx_Yellow_C','Coupe RB'),
            ('BP_McLarenGT_St_white_C', 'Coupe RB'),
            ('BP_McLarenGT_St_black_C', 'Coupe RB'),
            ('BP_Vantage_LGD_C',        'Coupe RB'),
            ('BP_Vantage_EP_C',         'Coupe RB'),
            ('BP_Countach_ULT_C',       'Coupe RB'),
            ('BP_Classic_01_C',         'Coupe RB'),
            ('BP_Classic_02_C',         'Coupe RB'),
            
            ('BP_DBX_LGD_C', 'DBX707'),
            ('BP_Urus_EP_C', 'Urus'),
            ('BP_Urus_LGD_C','Urus'),
            ('BP_Mirado_A_01_C',        'Mirado'),
            ('BP_Mirado_A_02_C',        'Mirado'),
            ('BP_Mirado_A_03_C',        'Mirado'),
            ('BP_Mirado_A_04_C',        'Mirado'),
            ('BP_Mirado_A_05_C',        'Mirado'),
            ('BP_Mirado_A_03_Esports_C','Mirado'),
            ('BP_Mirado_Open_01_C',     'Mirado'),
            ('BP_Mirado_Open_02_C',     'Mirado'),
            ('BP_Mirado_Open_03_C',     'Mirado'),
            ('BP_Mirado_Open_04_C',     'Mirado'),
            ('BP_Mirado_Open_05_C',     'Mirado'),
            
            ('BP_Special_ElSolitario_C',        'Motorcycle'),
            ('BP_Motorbike_04_C',               'Motorcycle'),
            ('BP_Motorbike_04_Desert_C',        'Motorcycle'),
            ('BP_Motorbike_04_SideCar_C',       'Motorcycle (w/ Sidecar)'),
            ('BP_Motorbike_04_SideCar_Desert_C','Motorcycle (w/ Sidecar)'),
            ('BP_Motorbike_04_FBR1_C',          'Motorcycle (w/ Sidecar)'),
            ('BP_Motorbike_Solitario_C',        'Motorcycle'),
            ('BP_PanigaleV4S_LGD01_C',          'Motorcycle'),
            ('BP_PanigaleV4S_LGD02_C',          'Motorcycle'),
            ('BP_PanigaleV4S_LGD03_C',          'Motorcycle'),
            ('BP_PanigaleV4S_LGD04_C',          'Motorcycle'),
            ('BP_PanigaleV4S_EP01_C',           'Motorcycle'),
            ('BP_PanigaleV4S_EP02_C',           'Motorcycle'),
            ('BP_PanigaleV4S_EP03_C',           'Motorcycle'),
            ('BP_PanigaleV4S_EP04_C',           'Motorcycle'),
            
            
            ('BP_Motorglider_C',        'Motor Glider'),
            ('BP_Motorglider_Green_C',  'Motor Glider'),
            ('BP_Motorglider_Teal_C',   'Motor Glider'),
            ('BP_Motorglider_Blue_C',   'Motor Glider'),
            
            ('BP_Niva_01_C',        'Zima'),
            ('BP_Niva_02_C',        'Zima'),
            ('BP_Niva_03_C',        'Zima'),
            ('BP_Niva_04_C',        'Zima'),
            ('BP_Niva_05_C',        'Zima'),
            ('BP_Niva_06_C',        'Zima'),
            ('BP_Niva_07_C',        'Zima'),
            ('BP_Niva_Esports_C',   'Zima'),
            ('BP_PickupTruck_A_01_C',       'Pickup Truck'),
            ('BP_PickupTruck_A_02_C',       'Pickup Truck'),
            ('BP_PickupTruck_A_03_C',       'Pickup Truck'),
            ('BP_PickupTruck_A_04_C',       'Pickup Truck'),
            ('BP_PickupTruck_A_05_C',       'Pickup Truck'),
            ('BP_PickupTruck_A_esports_C',  'Pickup Truck'),
            ('BP_PickupTruck_B_01_C',       'Pickup Truck'),
            ('BP_PickupTruck_B_02_C',       'Pickup Truck'),
            ('BP_PickupTruck_B_03_C',       'Pickup Truck'),
            ('BP_PickupTruck_B_04_C',       'Pickup Truck'),
            ('BP_PickupTruck_B_05_C',       'Pickup Truck'),
            ('BP_Pillar_Car_C', 'Pillar Security Car'),
            ('BP_PonyCoupe_C', 'Pony Coupe'),
            ('BP_Porter_C', 'Porter'),
            ('BP_Scooter_01_A_C', 'Scooter'),
            ('BP_Scooter_02_A_C', 'Scooter'),
            ('BP_Scooter_03_A_C', 'Scooter'),
            ('BP_Scooter_04_A_C', 'Scooter'),
            ('BP_Snowbike_01_C', 'Snowbike'),
            ('BP_Snowbike_02_C', 'Snowbike'),
            ('BP_Snowmobile_01_C', 'Snowmobile'),
            ('BP_Snowmobile_02_C', 'Snowmobile'),
            ('BP_Snowmobile_03_C', 'Snowmobile'),
            ('BP_Special_FbrBike_C', 'Special FBR Bike'),
            ('BP_TukTukTuk_A_01_C', 'Tukshai'),
            ('BP_TukTukTuk_A_02_C', 'Tukshai'),
            ('BP_TukTukTuk_A_03_C', 'Tukshai'),
            ('BP_Van_A_01_C', 'Van'),
            ('BP_Van_A_02_C', 'Van'),
            ('BP_Van_A_03_C', 'Van'),
            ('Buggy_A_01_C', 'Buggy'),
            ('Buggy_A_02_C', 'Buggy'),
            ('Buggy_A_03_C', 'Buggy'),
            ('Buggy_A_04_C', 'Buggy'),
            ('Buggy_A_05_C', 'Buggy'),
            ('Buggy_A_06_C', 'Buggy'),
            ('Dacia_A_01_v2_C',         'Dacia 1300'),
            ('Dacia_A_01_v2_snow_C',    'Dacia 1300'),
            ('Dacia_A_02_v2_C',         'Dacia 1300'),
            ('Dacia_A_03_v2_C',         'Dacia 1300'),
            ('Dacia_A_03_v2_Esports_C', 'Dacia 1300'),
            ('Dacia_A_04_v2_C',         'Dacia 1300'),
            ('Uaz_A_01_C',          'UAZ'),
            ('Uaz_Armored_C',       'UAZ'),
            ('Uaz_B_01_C',          'UAZ'),
            ('Uaz_B_01_esports_C',  'UAZ'),
            ('Uaz_C_01_C',          'UAZ'),
            ('BP_Uaz_FBR_C',        'UAZ'),
            ('Uaz_Pillar_C',        'UAZ'),
            ('Boat_PG117_C', 'PG-117'),
            ('PG117_A_01_C', 'PG-117'),
            ('BP_PicoBus_C','PicoBus'),
            
            ('DummyTransportAircraft_C', 'C-130'),
            ('MortarPawn_C', 'Mortar'),
            ('EmergencyAircraft_Tiger_C', 'Emergency Aircraft'),
            ('ParachutePlayer_C', 'Parachute'),
            ('ParachutePlayer_Warmode_C', 'Parachute'),
            ('RedeployAircraft_DihorOtok_C', 'Helicopter'),
            ('RedeployAircraft_Tiger_C', 'Helicopter'),
            ('TransportAircraft_Chimera_C', 'Helicopter'),
            ('TransportAircraft_Tiger_C', 'Helicopter'),
            ('WarModeTransportAircraft_C', 'C-130'),
            ('BP_DO_Circle_Train_Merged_C',     'Train'),
            ('BP_DO_Line_Train_Dino_Merged_C',  'Train'),
            ('BP_DO_Line_Train_Merged_C',       'Train'),
            ('BP_EmergencyPickupVehicle_C',     'Emergency Pickup'),
        ]

        # 스킵할 값 목록
        skip_values = {
            'WarModeTransportAircraft_C',
            'BP_EmergencyPickupVehicle_C',
            'DummyTransportAircraft_C',
            'EmergencyAircraft_Tiger_C',
            'MortarPawn_C',
            'ParachutePlayer_C',
            'ParachutePlayer_Warmode_C',
            'RedeployAircraft_DihorOtok_C',
            'RedeployAircraft_Tiger_C',
            'TransportAircraft_Chimera_C',
            'TransportAircraft_Tiger_C'
            'TransportAircraft_FBR_01_C'
        }

        # Converting to dictionary for quick lookup
        mapping_dict = dict(mapping)

        # Filtering and transforming the list
        filtered_and_transformed_data = []
        for sublist in list:
            if sublist[6] not in skip_values:
                if sublist[6] in mapping_dict:
                    sublist[6] = mapping_dict[sublist[6]]
                filtered_and_transformed_data.append(sublist)

        # for i in filtered_and_transformed_data:
        #     print(i)

        speed_hack_value_record_list = []
        sorted_list = sorted(filtered_and_transformed_data, key=lambda x: datetime.strptime(x[-2], '%Y-%m-%dT%H:%M:%S.%fZ'))
        for i in range(1, len(sorted_list)):
            # print(list[i])
            distance = ((sorted_list[i][2] - sorted_list[i-1][2])**2 + (sorted_list[i][3] - sorted_list[i-1][3])**2 + (sorted_list[i][4] - sorted_list[i-1][4])**2)**(1/2)
            time_diff = datetime.strptime(sorted_list[i][-2], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.strptime(sorted_list[i-1][-2], "%Y-%m-%dT%H:%M:%S.%fZ")
            time_diff_seconds = time_diff.total_seconds()

            if time_diff_seconds != 0:
                speed_cm_per_sec = distance / time_diff_seconds
            else:
                speed_cm_per_sec = 0 
            
            km_per_hour = (speed_cm_per_sec * 36) / 1000
            
            # speed_hack_key_record = {
            #     "match_id" : self.match_id,
            #     "player_id" : sorted_list[i][1]
            # }
            if km_per_hour < 300:
                speed_hack_value_record = {
                    "account_id" : self.account_id,
                    "vehicle_id" : sorted_list[i][6], # vehicle_id
                    # datetime.strptime(sorted_list[i][7], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S.%f'),
                    # datetime.strptime(sorted_list[i-1][7], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S.%f'),
                    # sorted_list[i][2],
                    # sorted_list[i-1][2],
                    # sorted_list[i][3],
                    # sorted_list[i-1][3],
                    # sorted_list[i][4],
                    # sorted_list[i-1][4],
                    # distance,
                    "time_diff" : time_diff_seconds,
                    # sorted_list[i][8], # event_log
                    # speed_cm_per_sec,
                    "km_per_h" : km_per_hour
                }
                speed_hack_value_record_list.append(speed_hack_value_record)
        print("dataPreProcess : ",len(speed_hack_value_record_list))
        # print(speed_hack_key_record)
        # print(speed_hack_value_record_list)
        return speed_hack_value_record_list

# def main(account_id, match_id, platform):
#     PRM = postReqestMLSpeed(account_id, match_id, platform)
#     process1 = PRM.makedictPerPlayer()
#     process2, xy_location_list = PRM.makeListFromDict(process1)
#     process3 = PRM.fill_vehicle_na(process2)
#     process4 = PRM.throwParachute(process3)
#     process5 = PRM.fill_walk(process4)
#     speed_hack_key_record, speed_hack_value_record = PRM.dataPreProcessForML(process5)

#     return speed_hack_key_record, speed_hack_value_record, xy_location_list
# def main(account_id, match_id, platform):
#     PRM = postRequestML(account_id,match_id, platform)
#     match_json, tele_json, current_tier = PRM.create_rsj_and_match_and_telemetry()
#     MLUser_record_key, MLUser_record_value = PRM.createMLUserRecord(match_json,tele_json,account_id,match_id,current_tier)
#     shot_record_key, shot_record_value_list = PRM.produceShotRecord(tele_json,account_id,match_id)

#     print(MLUser_record_key)
#     print(MLUser_record_value)
#     print(shot_record_key)
#     print(shot_record_value_list)
#     return MLUser_record_key, MLUser_record_value, shot_record_key, shot_record_value_list

# def post_request_preprocess(account_id, match_id):
#     total_radar_list = []
#     total_landing_loc = []
#     total_return_dict = {}
#     PRT = postRequestPreprocess(account_id, match_id)
#     match_json = PRT.createMatchJsonData()
#     matches_values, telemetryURL, mode, player_list = PRT.createMatchesjson(match_json)
#     tele_json = PRT.createTelemetryData(telemetryURL)
    
#     final_match_user_values = None

#     print("player_list :", len(player_list))
#     for player in player_list:
#         match_user_values, matchUser_radar_data_list, landing_loc ,match_id, map_id = PRT.createMatchUserJson(player, tele_json, match_json, mode)
#         # print(landing_loc)
#         total_radar_list.append(matchUser_radar_data_list)
#         total_landing_loc.append(landing_loc)
#         if match_user_values['account_id'] == account_id:
#             final_match_user_values = match_user_values

#     if final_match_user_values is None:
#         raise ValueError(f"No match found for account_id {account_id}")
#     total_return_dict = {
#             "match_id": match_id,
#             "map_id": map_id,
#             "players_data" : total_landing_loc
#     }
#     # print(total_landing_loc)
#     # print("number of total_landing_loc :",len(total_landing_loc))
#     print('match_id : ',total_return_dict['match_id'])
#     print('map_id : ',total_return_dict['map_id'])
#     for i in total_return_dict["players_data"]:
#         print('account_id : ', i['account_id'])
#         print('total_shots : ', i['total_shots'])
#         print('landing_coordinates_x : ',i['landing_coordinates_x'])
#         print('landing_coordinates_y : ',i['landing_coordinates_y'])
#     final_data = PRT.avgAndStd(matches_values, total_radar_list)
#     return final_data, final_match_user_values, total_return_dict

# if __name__ == "__main__":
#     account_id = "account.06bff4cad3a44c4a9c746a4b98e9003b"
#     match_id = 'd49c4e43-3331-41a3-a816-8eda935f5e7d'
#     platform = "steam"
#     main(account_id, match_id, platform)

