from datetime import datetime

class datapreProcessorForML:
    def __init__(self,playerName):
        self.player_name = playerName
        # self.match_id = None
    # def getMatchID(self,data):
    #     match_id = data[0]['MatchId'].split(".")[-1]
    #     print(match_id)
    #     return match_id
    
    def makedictPerPlayer(self,data):
        player_dict = []
        for i in data:
            try:
                if i['character']['name'] == self.player_name: 
                    player_dict.append(i)

            except:
                pass
        for i in data:
            try:
                if i['attacker']['name'] == self.player_name:
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
                                if i['character']['name'] == self.player_name:
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
                                if i['attacker']['name'] == self.player_name:
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
                                if i['character']['name'] == self.player_name:
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
                                if i['attacker']['name'] == self.player_name:
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
                                if i['character']['name'] == self.player_name:
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
                                if i['attacker']['name'] == self.player_name:
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
        return player_list


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

    def dataPreProcessForML(self,list,json_data,matchId):
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

        results = []
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
            
            result = (
                matchId,
                sorted_list[i][0], # player_name
                sorted_list[i][1], # player_id
                sorted_list[i][6], # vehicle_id
                datetime.strptime(sorted_list[i][7], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S.%f'),
                datetime.strptime(sorted_list[i-1][7], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S.%f'),
                sorted_list[i][2],
                sorted_list[i-1][2],
                sorted_list[i][3],
                sorted_list[i-1][3],
                sorted_list[i][4],
                sorted_list[i-1][4],
                distance,
                time_diff_seconds,
                sorted_list[i][8], # event_log
                speed_cm_per_sec,
                km_per_hour
            )
            results.append(result)
        # print("dataPreProcess : ",len(results))
        # for i in results[:1]:
        #     print(i)
        return results