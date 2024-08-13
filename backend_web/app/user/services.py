import re
from datetime import datetime
import requests


pubg_API_key = ("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
                "eyJqdGkiOiIwNjlhODVmMC0wYWMyLTAxM2QtY2QwYy0zM"
                "mFkODc5M2Q4OGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF"
                "0IjoxNzE4MTgwMjAzLCJwdWIiOiJibHVlaG9sZSIsInRpdG"
                "xlIjoicHViZyIsImFwcCI6Ii1lN2M4ZGIzMC02YjYxLTQyN"
                "mUtOTAyNy00M2Q3ZDI0MDQzMzEifQ.l-5N173ehGmo1d7XB"
                "gYLhF7ZZ2LeuwB9wprdQ1Oy6t8")
current_season = "division.bro.official.pc-2018-31"


def check_api_server():
    url = "https://api.pubg.com/status"
    headers = {"accept": "application/vnd.api+json"}

    check_response = requests.get(url, headers=headers)

    return check_response.status_code


def call_players_api_by_nickname(shard, nickname):
    url = f"https://api.pubg.com/shards/{shard}/players"
    querystring = {"filter[playerNames]": nickname}
    headers = {
        "accept": "application/vnd.api+json",
        "Authorization": pubg_API_key
    }

    players_response = requests.get(url, headers=headers, params=querystring)

    return players_response


def get_account_id_from_players_api_response(players_response):
    return players_response.json()['data'][0]['id']


def get_shard_from_players_api_response(players_response):
    return players_response.json()['data'][0]['attributes']['shardId']


def get_match_id_list_from_players_api_response(players_response):
    matches_raw = players_response.json()['data'][0]['relationships']['matches']['data']
    match_ids = []
    for match_raw in matches_raw:
        match_ids.append(match_raw['id'])
    return match_ids


def call_ranked_stats_api_by_account_id(shard, account_id):
    url = f"https://api.pubg.com/shards/{shard}/players/{account_id}/seasons/{current_season}/ranked"
    headers = {
        "accept": "application/vnd.api+json",
        "Authorization": pubg_API_key
    }

    ranked_stats_response = requests.get(url, headers=headers)

    return ranked_stats_response


def jsonify_ranked_stats_from_api(nickname, ranked_stats_response):
    user_result = {}

    account_id = ranked_stats_response.json()['data']['relationships']['player']['data']['id']
    season_id = ranked_stats_response.json()['data']['relationships']['season']['data']['id']
    shard = re.search(r'shards/(.*?)/players', ranked_stats_response.json()['links']['self']).group(1)
    latest_update = datetime.now().isoformat()

    ranked_game_mode_stats = ranked_stats_response.json()['data']['attributes']['rankedGameModeStats']
    if 'squad' in ranked_game_mode_stats:
        squad_stat_raw = ranked_game_mode_stats['squad']
        squad_stat = {}
        squad_stat['latest_nickname'] = nickname
        squad_stat['account_id'] = account_id
        squad_stat['season_id'] = season_id
        squad_stat['mode_id'] = 'squad'
        squad_stat['shard'] = shard
        squad_stat['current_rp'] = squad_stat_raw['currentRankPoint']
        squad_stat['best_rp'] = squad_stat_raw['bestRankPoint']
        squad_stat['current_tier'] = squad_stat_raw['currentTier']['tier']
        squad_stat['current_subtier'] = squad_stat_raw['currentTier']['subTier']
        squad_stat['best_tier'] = squad_stat_raw['bestTier']['tier']
        squad_stat['best_subtier'] = squad_stat_raw['bestTier']['subTier']
        squad_stat['play_count'] = squad_stat_raw['roundsPlayed']
        squad_stat['avg_rank'] = squad_stat_raw['avgRank']
        squad_stat['top10s'] = int(round(squad_stat_raw['top10Ratio'] * squad_stat_raw['roundsPlayed']))
        squad_stat['wins'] = squad_stat_raw['wins']
        squad_stat['kills'] = squad_stat_raw['kills']
        squad_stat['assists'] = squad_stat_raw['assists']
        squad_stat['deaths'] = squad_stat_raw['deaths']
        squad_stat['knockdowns'] = squad_stat_raw['dBNOs']
        squad_stat['total_damage'] = squad_stat_raw['damageDealt']
        squad_stat['kda'] = squad_stat_raw['kda']
        squad_stat['latest_update'] = latest_update
        user_result['squad'] = squad_stat

    if 'squad-fpp' in ranked_game_mode_stats:
        squad_fpp_stat_raw = ranked_game_mode_stats['squad-fpp']
        squad_fpp_stat = {}
        squad_fpp_stat['latest_nickname'] = nickname
        squad_fpp_stat['account_id'] = account_id
        squad_fpp_stat['season_id'] = season_id
        squad_fpp_stat['mode_id'] = 'squad-fpp'
        squad_fpp_stat['shard'] = shard
        squad_fpp_stat['current_rp'] = squad_fpp_stat_raw['currentRankPoint']
        squad_fpp_stat['best_rp'] = squad_fpp_stat_raw['bestRankPoint']
        squad_fpp_stat['current_tier'] = squad_fpp_stat_raw['currentTier']['tier']
        squad_fpp_stat['current_subtier'] = squad_fpp_stat_raw['currentTier']['subTier']
        squad_fpp_stat['best_tier'] = squad_fpp_stat_raw['bestTier']['tier']
        squad_fpp_stat['best_subtier'] = squad_fpp_stat_raw['bestTier']['subTier']
        squad_fpp_stat['play_count'] = squad_fpp_stat_raw['roundsPlayed']
        squad_fpp_stat['avg_rank'] = squad_fpp_stat_raw['avgRank']
        squad_fpp_stat['top10s'] = int(round(squad_fpp_stat_raw['top10Ratio'] * squad_fpp_stat_raw['roundsPlayed']))
        squad_fpp_stat['wins'] = squad_fpp_stat_raw['wins']
        squad_fpp_stat['kills'] = squad_fpp_stat_raw['kills']
        squad_fpp_stat['assists'] = squad_fpp_stat_raw['assists']
        squad_fpp_stat['deaths'] = squad_fpp_stat_raw['deaths']
        squad_fpp_stat['knockdowns'] = squad_fpp_stat_raw['dBNOs']
        squad_fpp_stat['total_damage'] = squad_fpp_stat_raw['damageDealt']
        squad_fpp_stat['kda'] = squad_fpp_stat_raw['kda']
        squad_fpp_stat['latest_update'] = latest_update
        user_result['squad-fpp'] = squad_fpp_stat

    if 'solo' in ranked_game_mode_stats:
        solo_stat_raw = ranked_game_mode_stats['solo']
        solo_stat = {}
        solo_stat['latest_nickname'] = nickname
        solo_stat['account_id'] = account_id
        solo_stat['season_id'] = season_id
        solo_stat['mode_id'] = 'solo'
        solo_stat['shard'] = shard
        solo_stat['current_rp'] = solo_stat_raw['currentRankPoint']
        solo_stat['best_rp'] = solo_stat_raw['bestRankPoint']
        solo_stat['current_tier'] = solo_stat_raw['currentTier']['tier']
        solo_stat['current_subtier'] = solo_stat_raw['currentTier']['subTier']
        solo_stat['best_tier'] = solo_stat_raw['bestTier']['tier']
        solo_stat['best_subtier'] = solo_stat_raw['bestTier']['subTier']
        solo_stat['play_count'] = solo_stat_raw['roundsPlayed']
        solo_stat['avg_rank'] = solo_stat_raw['avgRank']
        solo_stat['top10s'] = int(round(solo_stat_raw['top10Ratio'] * solo_stat_raw['roundsPlayed']))
        solo_stat['wins'] = solo_stat_raw['wins']
        solo_stat['kills'] = solo_stat_raw['kills']
        solo_stat['assists'] = solo_stat_raw['assists']
        solo_stat['deaths'] = solo_stat_raw['deaths']
        solo_stat['knockdowns'] = solo_stat_raw['dBNOs']
        solo_stat['total_damage'] = solo_stat_raw['damageDealt']
        solo_stat['kda'] = solo_stat_raw['kda']
        solo_stat['latest_update'] = latest_update
        user_result['solo'] = solo_stat

    if 'solo-fpp' in ranked_game_mode_stats:
        solo_fpp_stat_raw = ranked_game_mode_stats['solo-fpp']
        solo_fpp_stat = {}
        solo_fpp_stat['latest_nickname'] = nickname
        solo_fpp_stat['account_id'] = account_id
        solo_fpp_stat['season_id'] = season_id
        solo_fpp_stat['mode_id'] = 'solo-fpp'
        solo_fpp_stat['shard'] = shard
        solo_fpp_stat['current_rp'] = solo_fpp_stat_raw['currentRankPoint']
        solo_fpp_stat['best_rp'] = solo_fpp_stat_raw['bestRankPoint']
        solo_fpp_stat['current_tier'] = solo_fpp_stat_raw['currentTier']['tier']
        solo_fpp_stat['current_subtier'] = solo_fpp_stat_raw['currentTier']['subTier']
        solo_fpp_stat['best_tier'] = solo_fpp_stat_raw['bestTier']['tier']
        solo_fpp_stat['best_subtier'] = solo_fpp_stat_raw['bestTier']['subTier']
        solo_fpp_stat['play_count'] = solo_fpp_stat_raw['roundsPlayed']
        solo_fpp_stat['avg_rank'] = solo_fpp_stat_raw['avgRank']
        solo_fpp_stat['top10s'] = int(round(solo_fpp_stat_raw['top10Ratio'] * solo_fpp_stat_raw['roundsPlayed']))
        solo_fpp_stat['wins'] = solo_fpp_stat_raw['wins']
        solo_fpp_stat['kills'] = solo_fpp_stat_raw['kills']
        solo_fpp_stat['assists'] = solo_fpp_stat_raw['assists']
        solo_fpp_stat['deaths'] = solo_fpp_stat_raw['deaths']
        solo_fpp_stat['knockdowns'] = solo_fpp_stat_raw['dBNOs']
        solo_fpp_stat['total_damage'] = solo_fpp_stat_raw['damageDealt']
        solo_fpp_stat['kda'] = solo_fpp_stat_raw['kda']
        solo_fpp_stat['latest_update'] = latest_update
        user_result['solo-fpp'] = solo_fpp_stat

    return user_result
