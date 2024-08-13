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
        self.id_response = requests.get(self.id_search_by_nickname_url + self.playerName, headers=self.apis_header)

    def getPlayerId(self):
        while True:
            try:
                playerId = self.id_response.json()['data'][0]['links']['self'].split("/")[-1]
                return playerId
            except KeyError as e:
                print(f"KeyError: {e}")
                print("JSON response:", self.id_response.json())
                if 'data' in str(e):
                    print(f"경고 : 플레이어 {self.playerName}에 대한 정보가 없습니다. 닉네임을 변경했거나 계정을 삭제했을 수 있습니다. 무시하고 진행합니다...")
                    return None
            except json.JSONDecodeError as e:
                print("Json 디코딩 실패. API 호출 제한에 걸렸을 수 있습니다. 15초 후 재시도 합니다.")
                time.sleep(15)
                self.id_response = requests.get(self.id_search_by_nickname_url + self.playerName, headers=self.apis_header)
                
    def getMatchIdList(self):
        match_datas = self.id_response.json()['data'][0]['relationships']['matches']['data']
        match_data_lists = [match['id'] for match in match_datas]
        print(f"검색된 matchId 수 : {len(match_data_lists)}")
        return match_data_lists
    
    def getTelemetryURLFromList(self, match_data_lists):
        match_search_by_matchId_url = f"https://api.pubg.com/shards/{self.platform}/matches/"
        telemetryURLList = []
        for match_IDs in match_data_lists:
            match_data = requests.get(match_search_by_matchId_url + match_IDs, headers=self.apis_header,params=self.params)
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
    
    def getOtherApiToJson(self, endPoints,platform):
        url = "https://api.pubg.com/shards/"+ platform + "/" + endPoints 
        print(url)
        while True:
            try:
                response = requests.get(url, headers=self.apis_header)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if '404' in str(e):
                    print('404 Error 요청한 주소를 찾을 수 없습니다')
                    return e
                else:
                    print(f"요청 실패 : {e}, 15초 후 재시도 합니다.")
                    time.sleep(15)
            except json.JSONDecodeError as e:
                print("Json 디코딩 실패. API 호출 제한에 걸렸을 수 있습니다. 15초 후 재시도 합니다.")
                time.sleep(15)