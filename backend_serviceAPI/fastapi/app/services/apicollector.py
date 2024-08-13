import requests
import json
import time

class getApiToJson:
    def __init__(self, platform, playerName, apikey):
        self.platform = platform
        self.playerName = playerName
        self.apikey = apikey
        self.id_search_by_nickname_url = f"https://api.pubg.com/shards/{self.platform}/players?filter[playerNames]="
        self.apis_header = {
            "Authorization": f"Bearer {self.apikey}",
            "Accept": "application/vnd.api+json"
        }
        self.telemetry_header = {
            "Accept": "application/vnd.api+json",
            "Accept-Encoding": "gzip"
        }
        print(self.apis_header)
        self.id_response = requests.get(self.id_search_by_nickname_url + self.playerName, headers=self.apis_header)

    def getPlayerId(self):
        while True:
            try:
                playerId = self.id_response.json()['data'][0]['links']['self'].split("/")[-1]
                return playerId
            except KeyError as e:
                print(f"KeyError: {e}")
                # print("JSON response:", self.id_response.json())
                if 'data' in str(e):
                    print(f"Warning : No data in player {self.playerName}. maybe account is deleted. ignoring...")
                    return None
            except json.JSONDecodeError as e:
                print("Fail to Json Decoding. Maybe Api limit exceed. retrying in 15 sec...")
                time.sleep(15)
                self.id_response = requests.get(self.id_search_by_nickname_url + self.playerName, headers=self.apis_header)
                
    def getMatchIdList(self):
        try:
            match_datas = self.id_response.json()['data'][0]['relationships']['matches']['data']
            # print(match_datas)
            match_data_lists = [match['id'] for match in match_datas]
            print(f"검색된 matchId 수 : {len(match_data_lists)}")
            return match_data_lists
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error while getting match ID list: {e}")
            return []
    
    def getTelemetryURLFromList(self, match_data_lists):
        match_search_by_matchId_url = f"https://api.pubg.com/shards/{self.platform}/matches/"
        telemetryURLList = []
        for match_IDs in match_data_lists:
            match_data = requests.get(match_search_by_matchId_url + match_IDs, headers=self.apis_header)
            telemetryId = match_data.json()['data']['relationships']['assets']['data'][0]['id']
            print(f"matchId : {match_IDs}\ntelemetryId : {telemetryId}")
            for included_item in match_data.json()['included']:
                if included_item['type'] == 'asset':
                    telemetry_url = included_item['attributes']['URL']
                    telemetryURLList.append(telemetry_url)
                    print(telemetry_url, "\n")
        return telemetryURLList
    
    def getTelemtryJsonFromTelemetryURL(self, telemetry_url):
        telemetry_response = requests.get(telemetry_url, headers=self.telemetry_header)
        return telemetry_response.json()
    
    def getTelemetryJsonFromMatchId(self, matchId):
        self.matchId = matchId
        match_search_by_matchId_url = f"https://api.pubg.com/shards/{self.platform}/matches/"
        match_data = requests.get(match_search_by_matchId_url + self.matchId, headers=self.apis_header)
        for included_item in match_data.json()['included']:
            if included_item['type'] == 'asset':
                self.telemetryURL = included_item['attributes']['URL']
        # print(f"matchId : {self.matchId}\ntelemetryURL : {self.telemetryURL}\n")
        telemetry_response = requests.get(self.telemetryURL, headers=self.telemetry_header)
        return telemetry_response.json()
    
    def saveJsonFile(self, JsonResponse, fileName, filetype):
        filetype = "." + f"filetype"
        self.fileName = fileName + filetype
        with open(self.fileName, 'w') as json_file:
            json.dump(JsonResponse, json_file, indent=4)
    
    def getOtherApiToJson(self, endPoints):
        url = "https://api.pubg.com/shards/"+self.platform + endPoints
        while True:
            try:
                response = requests.get(url, headers=self.apis_header)
                response.raise_for_status()
                print("Get API Response Status Code : ",response.status_code)
                return response.json()
            except requests.exceptions.RequestException as e:
                if '404' in str(e):
                    print('404 Error')
                    return e
                else:
                    print(f"error : {e}, retrying in 15 sec...")
                    time.sleep(15)
            except json.JSONDecodeError as e:
                print("Fail to Json Decoding. Maybe Api limit exceed. retrying in 15 sec...")
                time.sleep(15)

# platform  = 'steam'
# playerName = 'egunmotchamzi'
# apikey = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIwOTczZWUxMC0wOTZlLTAxM2QtY2NlNi0zMmFkODc5M2Q4OGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzE4MDM0MTc4LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImhlaGViYWxzc2EifQ.ADpdC0UInjTkDeVJXNjtZvMf4rNQAyrzQqWuPGvuteE'
# GA = getApiToJson(platform, playerName, apikey)

# account_id = GA.getPlayerId()
# print(account_id)
# match_id_list = GA.getMatchIdList()

# for match_id in match_id_list:
#     match_json = GA.getOtherApiToJson('/matches/' + match_id)
#     if match_json['data']['attributes']['matchType'] != "competitive":
#         print("경쟁전 아님. 스킵함")
#     else:
#         print(match_id)