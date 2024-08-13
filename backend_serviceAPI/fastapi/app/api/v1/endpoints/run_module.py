import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.moduleWorkerV2 import main
from app.services.run import post_request_preprocess, post_request_ml_shot, post_request_ml_speed
from app.services.playerNames import player_nicknames
import random
import threading
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

class PreprocessRequest(BaseModel):
    playerID: str
    matchID: str
    shardID: str

class MLRequestAim(BaseModel):
    playerID: str
    matchID: str
    shardID: str

class MLRequestSpeed(BaseModel):
    playerID: str
    matchID: str
    shardID: str

class MLRequest(BaseModel):
    playerID: str
    matchID: str
    shardID: str    

# 모듈 실행을 위한 스레드와 플래그 변수
module_thread = None
module_running = False
module_lock = threading.Lock()

def run_module_thread():
    global module_running
    while module_running:
        player_name = random.choice(player_nicknames)
        try:
            execute_run_module(player_name, platform='steam')
        except Exception as e:
            logger.error(f"Module run failed with platform 'steam': {e}")
            try:
                execute_run_module(player_name, platform='kakao')
            except Exception as e2:
                logger.error(f"Module run failed with platform 'kakao' as well: {e2}")
        time.sleep(1)  # 1초 대기 후 다음 이름 선택 및 실행

def execute_run_module(player_name, platform):
    main(
        kafka_broker='10.11.10.58:9092',
        schema_registry_url='http://10.11.10.58:8081',
        platform=platform,
        playerName=player_name,
        api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIwOTczZWUxMC0wOTZlLTAxM2QtY2NlNi0zMmFkODc5M2Q4OGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzE4MDM0MTc4LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImhlaGViYWxzc2EifQ.ADpdC0UInjTkDeVJXNjtZvMf4rNQAyrzQqWuPGvuteE',
        current_season='division.bro.official.pc-2018-31',
        matches_endpoint='/matches/'
    )
    logger.info(f"Module run complete with platform '{platform}'")

@router.post("/run")
def run_module():
    global module_thread, module_running

    with module_lock:
        if module_running:
            raise HTTPException(status_code=400, detail="Module is already running. Please stop the module before starting a new one.")
        module_running = True

    module_thread = threading.Thread(target=run_module_thread)
    module_thread.start()

    logger.info("run_module endpoint was called")
    return {"status": "Module started"}

@router.post("/stop")
def stop_module():
    global module_thread, module_running

    with module_lock:
        if not module_running:
            raise HTTPException(status_code=400, detail="Module is not running. Please start the module before attempting to stop it.")
        module_running = False

    if module_thread:
        module_thread.join()

    logger.info("stop_module endpoint was called")
    return {"status": "Module stopped"}

@router.post("/preprocess")
def preprocess_module(request: PreprocessRequest):
    try:
        account_id = request.playerID
        match_id = request.matchID
        shard_id = request.shardID
        final_data = post_request_preprocess(account_id, match_id, shard_id)
        return final_data
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preprocessing failed {e}")

@router.post("/shot")
def ml_shot(request: MLRequestAim):
    try:
        account_id = request.playerID
        match_id = request.matchID
        shard_id = request.shardID
        MLUser_record_value, shot_record_value_list = post_request_ml_shot(account_id,match_id,shard_id)
        aim_hack = {
            "for_ml_user" : MLUser_record_value,
            "shot" : shot_record_value_list
        }
        return aim_hack
    except Exception as e:
        logger.error(f"ML Shot Preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"ML Shot Preprocessing failed {e}")
    
@router.post("/speed")
def ml_speed(request: MLRequest):
    try:
        account_id = request.playerID
        match_id = request.matchID
        shard_id = request.shardID
        speed_hack_value_record, xy_location_list = post_request_ml_speed(account_id,match_id,shard_id)
        speed_hack_dict = {
            "speed_hack" : speed_hack_value_record,
            "xy_location" :xy_location_list
        }
        return speed_hack_dict
    except Exception as e:
        logger.error(f"ML Speed Preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"ML Speed Preprocessing failed {e}")
    
@router.post("/ml")
def all_ml(request: MLRequest):
    try:
        account_id = request.playerID
        match_id = request.matchID
        shard_id = request.shardID
        MLUser_record_value, shot_record_value_list = post_request_ml_shot(account_id,match_id,shard_id)
        speed_hack_value_record, xy_location_list = post_request_ml_speed(account_id,match_id,shard_id)
        final_result_dict = {
            "for_ml_user" : MLUser_record_value,
            "shot" : shot_record_value_list,
            "speed_hack" : speed_hack_value_record,
            "xy_location" :xy_location_list
        }
        return final_result_dict
    except Exception as e:
        logger.error(f"ML Shot Preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"ML Shot Preprocessing failed {e}")