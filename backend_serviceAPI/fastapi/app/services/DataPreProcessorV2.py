from datetime import datetime

class preprocessor:
    def __init__(self, accountId, seasonId, platform, playerName):
        self.accountId = accountId
        self.seasonId = seasonId
        self.platform = platform
        self.playerName = playerName
        self.mode = None
        self.matchId = None

    def createAndProduceUsersRecord(self,ranked_stats_json,kafkaConnector):
        print("############################## process def : createUsersRecord ##############################")
        key_wave = ranked_stats_json['data']['attributes']['rankedGameModeStats']
        mode_list = list(key_wave.keys()) 
        current_tier = ""
        for i in mode_list:
            mode = i
            currentRankPoint, bestRankPoint, currentTier_tier, currentTier_subTier, bestTier_tier, bestTier_subTier, play_count, avgRank, \
                top10s, wins, kills, assists, deaths, knockdowns, damageDealt, kda  =\
            key_wave[i]['currentRankPoint'],\
            key_wave[i]['bestRankPoint'],\
            key_wave[i]['currentTier']['tier'],\
            key_wave[i]['currentTier']['subTier'],\
            key_wave[i]['bestTier']['tier'],\
            key_wave[i]['bestTier']['subTier'],\
            key_wave[i]['roundsPlayed'],\
            key_wave[i]['avgRank'],\
            int(round(key_wave[i]['top10Ratio']*key_wave[i]['roundsPlayed'])),\
            key_wave[i]['wins'],\
            key_wave[i]['kills'],\
            key_wave[i]['assists'],\
            key_wave[i]['deaths'],\
            key_wave[i]['dBNOs'],\
            key_wave[i]['damageDealt'],\
            key_wave[i]['kda']
            # Get the current datetime object
            latest_update = datetime.now().isoformat()
            # Convert the datetime object to a timestamp and multiply by 1000 to get milliseconds
            # latest_update = int(time.mktime(latest_update_dt.timetuple()) * 1000)
            user_record_key = {"account_id": self.accountId, "season_id": self.seasonId, "mode_id": mode}

            user_record_value = {
                "account_id": self.accountId,
                "season_id": self.seasonId,
                "mode_id": mode,
                "latest_nickname": self.playerName,
                "shard": self.platform,
                "current_rp": currentRankPoint,
                "best_rp": bestRankPoint,
                "current_tier": currentTier_tier,
                "current_subtier": currentTier_subTier,
                "best_tier": bestTier_tier,
                "best_subtier": bestTier_subTier,
                "play_count": play_count,
                "avg_rank": avgRank,
                "top10s": top10s,
                "wins": wins,
                "kills": kills,
                "assists": assists,
                "deaths": deaths,
                "knockdowns": knockdowns,
                "total_damage": damageDealt,
                "kda": kda,
                "latest_update" : latest_update
                }
            # for key,value in user_record_value.items():
            #     print(key, ":", value)
            # print("##############user_record_value###############")
            # print(user_record_value)

            kafkaConnector.produce_users_message(user_record_key, user_record_value)
        return currentTier_tier

    def createMatchesRecord(self,json_data):
        print("############################## process def : createMatchesRecord ##############################")
        self.matchId = json_data['data']['id']
        key_wave = json_data['data']['attributes']
        self.mode = key_wave['gameMode']
        shard = key_wave['shardId']
        map = key_wave['mapName']
        played_at = key_wave['createdAt']
        played_at = datetime.strptime(key_wave['createdAt'],"%Y-%m-%dT%H:%M:%SZ")
        played_at = played_at.strftime("%Y-%m-%d %H:%M:%S")
        # played_at = int(time.mktime(played_at.timetuple()) * 1000)
        duration = int(key_wave['duration'])
        for include in json_data['included']:
            if include['type'] == 'asset':
                telemetryURL = include['attributes']['URL']
                
        matches_record_key = {"match_id": self.matchId}

        # print("match_id : ",        self.matchId)
        # print("mode_id : " ,        self.mode)
        # print("shard : ",           shard)
        # print("map : ",             map)
        # print("played_at_millis :", played_at)
        # print("duration : ",        duration)
        # print("telemetryURL : ",    telemetryURL)
        # print("belligerence_avg : ",belligerence_avg)
        # print("belligerence_std : ",belligerence_std)
        # print("combat_avg : ", combat_avg)
        # print("combat_std" , combat_std)
        # print("viability_avg : ", viability_avg)
        # print("viability_std : ",viability_std)
        # print("utility_avg : ", utility_avg)
        # print("utility_std : ", utility_std)
        # print("sniping_avg : ", sniping_avg)
        # print("sniping_std : ", sniping_std)

        matches_record_value = {
            "match_id" :        self.matchId,
            "mode_id" :         self.mode,
            "season_id" :       self.seasonId,
            "shard" :           shard,
            "map_id" :          map,
            "duration" :        duration,
            "played_at" :       played_at,
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

        return matches_record_key, matches_record_value, telemetryURL, self.mode, self.matchId

    def createMatchUserRecord(self, tele_json_data, match_json_data, mode, matchId, account_id):
        print("############################## process def : createMatchUserRecord ##############################")
        self.matchId = matchId
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

        for i in tele_json_data:
            try:
                # print(f"Processing telemetry event: {i['_T']}")  # 디버깅 출력 추가
                if i['_T'] == "LogPlayerAttack" and i['attacker']['accountId'] == account_id and i['common']['isGame'] >= 0.1 and i['attackId'] >= 10000:
                    self.total_shots += 1
                if i['_T'] == 'LogPlayerTakeDamage' and i['damageTypeCategory'] == "Damage_Gun" and i['attacker']['accountId'] == account_id:
                    hit_count += 1 
                if i['_T'] == 'LogPlayerTakeDamage' and i['damageTypeCategory'] == 'Damage_VehicleHit' and i['attacker']['accountId'] == account_id:
                    hitByVehicle_damage += i['damage']
                elif i['_T'] == 'LogPlayerKillV2' and i['killer']['accountId'] == account_id:
                    kill_distance_list.append(i['killerDamageInfo']['distance'])
                elif i['_T'] == 'LogParachuteLanding' and i['character']['accountId'] == account_id and 0.1 <= i['common']['isGame'] <= 0.5:
                    landed_zone_x = i['character']['location']['x']
                    landed_zone_y = i['character']['location']['y']
                elif i['_T'] == 'LogPlayerUseThrowable' and i['attacker']['accountId'] == account_id:
                    throw_count += 1
                elif i['_T'] == ('LogVehicleRide' or i['_T'] == 'LogVehicleLeave') and i['character']['accountId'] == account_id and i['vehicle']['vehicleType'] != 'TransportAircraft':
                    vehicle_count += 1
            except KeyError as e:
                continue
                print(f"KeyError in for i in tele_json_data : {e}")
            except Exception as e:
                continue
                print(f"ExceptionError for i in tele_json_data : {e}")

        if len(kill_distance_list) == 0:
            avg_kill_distance = 0
            longest_kill_dist = 0
        else:
            avg_kill_distance = (sum(kill_distance_list) / len(kill_distance_list)) / 100
            longest_kill_dist = max(kill_distance_list) / 100

        if self.total_shots == 0:
            self.accuracy = 0
        else:
            self.accuracy = (hit_count / self.total_shots) * 100

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
                    total_distance = (rideDistance + swimDistance + walkDistance) / 100
            except KeyError as e:
                continue
                print(f"KeyError for i in match_json_data['included'] : {e}")
            except Exception as e:
                continue
                print(f"ExceptionError for i in match_json_data['included'] : {e}")

        # belligerence = None
        # combat = self.accuracy * 10 + self.kills * 50 + self.dBNOs + self.assists * 30 + longest_kill_dist
        # viability = survival_time + heals * 30 + boost_count * 30
        # utility = throw_count * 10 + vehicle_count * 0.5 + hitByVehicle_damage * 0.5
        # sniping = avg_kill_distance
                
        matchUser_record_key = {"account_id": account_id, "match_id" : self.matchId}

        matchUser_record_value = {
            "account_id":       str(account_id),
            "season_id" :       str(self.seasonId),
            "mode_id" :         str(self.mode),
            "match_id" :        str(self.matchId),
            "shard" :           str(self.platform),
            "total_shots":      int(self.total_shots),
            "total_distance":   float(total_distance),
            "kills":            int(self.kills),
            "assists":          int(self.assists),
            "ranking":          int(ranking),
            "revives":          int(revives),
            "longest_kill_dist":float(longest_kill_dist),
            "accuracy":         float(self.accuracy),
            "heal_count":       int(heals),
            "lifetime":         int(survival_time),
            "landed_location_x":float(landed_zone_x),
            "landed_location_y":float(landed_zone_y),
            "avg_kill_distance":float(avg_kill_distance),
            "damage_dealt":     float(self.damageDealt),
            "knockdowns":       int(self.dBNOs),
            "boost_count":      int(boost_count),
            "throw_count":      int(throw_count),
            "vehicle_use_count":int(vehicle_count),
            "damage_from_vehicle" : float(hitByVehicle_damage),
            "belligerence" :    None,
            "combat" :          None,
            "viability" :       None,
            "utility" :         None,
            "sniping" :         None
                }
        # for key, value in matchUser_record_value.items():
        #     print(key,":",value)
        return matchUser_record_key, matchUser_record_value, self.total_shots
    
    def createMLUserRecord(self,tele_json_data,accountId,matchId,currentTier_tier,total_shot):
        print("######################### process def : createMLUserRecord ################################")
        headshot_rate = 0
        hit_count = 0
        head_count = 0
        for i in tele_json_data:
            try:
                if i['_T'] == 'LogPlayerTakeDamage' and i['damageTypeCategory'] == "Damage_Gun" and i['attacker']['accountId'] == accountId:
                    hit_count += 1 
                if i['_T'] == 'LogPlayerTakeDamage' and i['damageTypeCategory'] == "Damage_Gun" and i['attacker']['accountId'] == accountId and i['damageReason'] == "HeadShot":
                    head_count+=1
            except KeyError as e:
                continue
                print(f"KeyError: {e}")
            except Exception as e:
                continue
                print(f"An error occurred: {e}")
        MLUser_record_key = {"account_id": accountId, "match_id" : matchId}
        MLUser_record_value = {
            "account_id": accountId,
            "match_id" : matchId,
            "current_tier" : currentTier_tier,
            "kills" : self.kills,
            "knockdowns" : self.dBNOs,
            "assists" : self.assists,
            "total_damage" : self.damageDealt,
            "total_shot" : int(total_shot),
            "hit_count" : int(hit_count),
            "head_shot" : int(head_count)
                }

        return MLUser_record_key, MLUser_record_value
    
    def produceShotRecord(self,json_data,kafkaConnector,accountId,matchId):
        print("######################### process def : produceShotRecord ################################")
        self.is_hit = False
        self.hit_point = None
        self.hit_distance = None
        attack_id = 0
        weapon_id = ""
        timeStamp = ""
        for i in json_data:
            try:
                if i['attacker']['accountId'] == accountId and i['common']['isGame'] >= 0.1 and i['weapon']['subCategory'] == "Main" and  i['_T'] == "LogPlayerAttack":
                    attack_id = int(i['attackId'])
                    weapon_id = str(i['weapon']['itemId'])
                    timeStamp = datetime.strptime(i['_D'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    timeStamp = timeStamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    # print(timeStamp)
                    for j in json_data:
                        if j['_T'] == "LogPlayerTakeDamage" and j['attackId'] == attack_id:
                            self.is_hit = True
                            self.hit_point = j['damageReason']
                            self.hit_distance = ((j['attacker']['location']['x']-j['victim']['location']['x'])**2 + (j['attacker']['location']['y']-j['victim']['location']['y'])**2 + (j['attacker']['location']['z']-j['victim']['location']['z'])**2)**(1/2)
                            break
                    shot_record_key = {"match_id" : matchId, "attack_id" : attack_id}
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
                    kafkaConnector.produce_shot_message(shot_record_key,shot_record_value)
                    self.is_hit = False
                    self.hit_point = None
                    self.hit_distance = None
            except KeyError as e:
                continue
                print("key Error :",e)
            except Exception as e:
                continue
                print("Exception Error :",e)
