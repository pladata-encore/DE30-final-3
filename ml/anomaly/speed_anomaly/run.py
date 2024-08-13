from speed_ml_predictor import call_ml_speed_data_api_by_account_id_match_id_shard,type_check,predict_outliers_for_user

# 예측 수행
account_id = ''  # 실제 account_id로 변경
match_id = ""
shard = ""
walk_model_path = "/home/ec2-user/web-backend/app/models/vehicle/walk_model.pkl" # walk pkl 파일 명시
vehicle_model_directory = "/home/ec2-user/web-backend/app/models/vehicle" # pkl 파일이 위치한 디렉토리

speed_json = call_ml_speed_data_api_by_account_id_match_id_shard(account_id, match_id, shard)
checked_speed_json = type_check(speed_json)

if ('/'.join(walk_model_path.split("/")[:-1]) != vehicle_model_directory) or (not walk_model_path.endswith(".pkl")) or (vehicle_model_directory != "/home/ec2-user/web-backend/app/models/vehicle"):
    print("File path error")
else:
    predictions = predict_outliers_for_user(account_id, walk_model_path, vehicle_model_directory,checked_speed_json)
    # 예측 결과 출력
    if predictions:
        for vehicle_id, result_df in predictions.items():
            print(f"Predictions for {vehicle_id}:")
            for _, row in result_df.iterrows():
                status = 'Outlier' if row['is_outlier'] else 'Normal'
                print(f"  Account ID: {row['account_id']}, Speed: {row['km_per_h']}, Status: {status}")
    else:
        print("No predictions available.")

