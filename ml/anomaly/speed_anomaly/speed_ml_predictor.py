import os
import pickle
import pandas as pd
import numpy as np
import logging
import requests

def call_ml_speed_data_api_by_account_id_match_id_shard(account_id, match_id, shard):
    url = "http://10.11.10.180:8000/api/v1/speed"
    data = {
        "playerID": account_id,
        "matchID": match_id,
        "shardID": shard
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        ml_speed_data_response = requests.post(url, json=data, headers=headers)
        ml_speed_data_response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        logging.info(f"API call successful for account_id: {account_id}, match_id: {match_id}, shard: {shard}")
        return ml_speed_data_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        return None

def type_check(data):
    data_1 = data.get("speed_hack",{})
    for item in data_1:
        # print("컬럼명 변경 감지")
        if 'km/h' in item:
            item['km_per_h'] = item.pop('km/h')
        else:
            continue
    return data_1

# 특정 유저의 비정상적인 스피드를 예측하는 함수
def predict_outliers_for_user(account_id, walk_model_path, vehicle_model_directory,data):
    # 유저의 데이터 로드
    # df = get_user_data(account_id)
    df = pd.DataFrame(data)
    if df.empty:
        print(f"No data found for account_id {account_id}.")
        return

    predictions = {}
    
    # 워크 로그 처리
    walk_df = df[df['vehicle_id'] == 'walk']
    if not walk_df.empty:
        if os.path.exists(walk_model_path):
            with open(walk_model_path, 'rb') as f:
                model, scaler = pickle.load(f)
            
            # 데이터 정규화 및 예측
            print(model,type(model),"##################################################")
            X_scaled = scaler.transform(walk_df[['km_per_h', 'time_diff']])
            walk_df['cluster'] = model.predict(X_scaled)

            # 클러스터 중심에서의 거리 계산
            centers = model.cluster_centers_
            walk_df['distance_to_center'] = [
                np.linalg.norm(X_scaled[idx] - centers[cluster]) 
                for idx, cluster in enumerate(walk_df['cluster'])
            ]

            # Z-Score 계산
            mean_distance = walk_df['distance_to_center'].mean()
            std_distance = walk_df['distance_to_center'].std()
            z_score_threshold = 3
            walk_df['z_score'] = (walk_df['distance_to_center'] - mean_distance) / std_distance
            walk_df['is_outlier'] = walk_df['z_score'].abs() > z_score_threshold
            
            predictions['walk'] = walk_df[['account_id', 'vehicle_id', 'km_per_h', 'is_outlier']]
        else:
            print("Walk model file not found.")

    # 차량 로그 처리
    vehicle_df = df[df['vehicle_id'] != 'walk']
    for vehicle_id, group_df in vehicle_df.groupby('vehicle_id'):
        model_path = os.path.join(vehicle_model_directory, f'{vehicle_id}_model.pkl')
        
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model, scaler = pickle.load(f)
            print(model,type(model),"##################################################")
            # 데이터 정규화 및 예측
            X_scaled = scaler.transform(group_df[['km_per_h', 'time_diff']])
            group_df['cluster'] = model.predict(X_scaled)

            # 클러스터 중심에서의 거리 계산
            centers = model.cluster_centers_
            group_df['distance_to_center'] = [
                np.linalg.norm(X_scaled[idx] - centers[cluster]) 
                for idx, cluster in enumerate(group_df['cluster'])
            ]

            # Z-Score 계산
            mean_distance = group_df['distance_to_center'].mean()
            std_distance = group_df['distance_to_center'].std()
            z_score_threshold = 3
            group_df['z_score'] = (group_df['distance_to_center'] - mean_distance) / std_distance
            group_df['is_outlier'] = group_df['z_score'].abs() > z_score_threshold

            predictions[vehicle_id] = group_df[['account_id', 'vehicle_id', 'km_per_h', 'is_outlier']]
        else:
            print(f"표본이 너무 적어서 {vehicle_id}의 예측을 수행할 수 없습니다.")

    return predictions
