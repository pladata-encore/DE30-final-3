from moduleWorkerfs import main


platform = 'steam'
# playerName = 'GuoZzz14'
api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJjZjA2NWM4MC0wYWIxLTAxM2QtY2QwOC0zMmFkODc5M2Q4OGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzE4MTczMjM3LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6Ii1hYmFmZjMzYy00Njc2LTRhY2YtODk2My1hNjA4NmRiNmRmNGQifQ.vJMxxR-La9M_ZP2DBiOLYy5SLrUSmRkNQcjdsCL3jSo'
current_season = 'division.bro.official.pc-2018-30'
matches_endpoint = 'matches/'
players_endpoint = 'players/'

# host = 'de30-final-3-db-mysql.cve6gqgcih9t.ap-northeast-2.rds.amazonaws.com' 
# database = 'de30_final_3'
# user = 'admin'         
# password = '72767276'       
# speedhack_table_ap = 'speed_hack_ap'

host = '127.0.0.1' 
database = 'speed_hack'
user = 'root'         
password = '1234'       
speedhack_table_ap = 'speed_hack_ap'

if __name__ == '__main__':
    main(platform,api_key,current_season,matches_endpoint,players_endpoint,host,database,user,password,speedhack_table_ap)