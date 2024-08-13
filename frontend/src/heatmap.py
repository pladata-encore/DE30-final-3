import streamlit as st
from matplotlib import pyplot as plt
import seaborn as sns
from PIL import Image
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import os
from sqlalchemy import create_engine

# 데이터 로드 함수 (필요에 따라 사용)
def load_data():
    # 여기에 실제로 데이터를 로드하는 코드 삽입 (예: RDS에서 로드)
    # matches_df와 match_user_df를 전역으로 불러오거나, 이 함수 내에서 처리할 수 있음
    matches_query = "SELECT season_id, match_id, map_id FROM matches"
    match_user_query = """
        SELECT match_id, landed_location_x, landed_location_y 
        FROM match_user
        WHERE landed_location_x IS NOT NULL AND landed_location_y IS NOT NULL
    """
    # 데이터베이스 연결 설정
    db_config = {
    'host': 'de30-final-3-db-mysql.cve6gqgcih9t.ap-northeast-2.rds.amazonaws.com',
    'user': 'admin',
    'password': '72767276',
    'database': 'de30_final_3',
}

    # SQLAlchemy 엔진 생성
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

    # 데이터 쿼리
    matches_df = pd.read_sql(matches_query, engine)
    match_user_df = pd.read_sql(match_user_query, engine)

    # 숫자형 변환
    match_user_df['landed_location_x'] = pd.to_numeric(match_user_df['landed_location_x'], errors='coerce')
    match_user_df['landed_location_y'] = pd.to_numeric(match_user_df['landed_location_y'], errors='coerce')

    return matches_df, match_user_df

# 데이터 클러스터링 및 시각화 함수
def process_and_cluster_map_data(map_name, match_user_df, matches_df, map_y_offsets):
    group = match_user_df[match_user_df['match_id'].map(matches_df.set_index('match_id')['map_id']) == map_name]

    # Y 좌표 오프셋 조정
    if map_name in map_y_offsets:
        offset = map_y_offsets[map_name]
        group['landed_location_y'] = offset - group['landed_location_y'].abs()

    # 특정 조건에 맞는 데이터 필터링 (x가 0이고 y는 816000 또는 408000인 데이터 제거)
    group = group[~((group['landed_location_x'] == 0) & (group['landed_location_y'].isin([816000, 408000])))]

    X = group[['landed_location_x', 'landed_location_y']]

    # 엘보우 기법을 사용하여 최적의 클러스터 수 찾기
    silhouette_scores = []
    for k in range(2, 11):
        kmeans = KMeans(n_clusters=k, random_state=1)
        labels = kmeans.fit_predict(X)
        silhouette = silhouette_score(X, labels)
        silhouette_scores.append((k, silhouette))

    best_k = max(silhouette_scores, key=lambda x: x[1])[0]

    # 최적의 k를 사용하여 KMeans 클러스터링
    kmeans = KMeans(n_clusters=best_k, random_state=1)
    group['cluster'] = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_

    return group, centers

# def plot_clusters(group, centers):
#     plt.figure(figsize=(10, 10))

#     # 클러스터링 결과를 플로팅
#     plt.scatter(group['landed_location_x'], group['landed_location_y'], c=group['cluster'], cmap='viridis', s=50, alpha=0.6)
    
#     # 클러스터 중심점 플로팅
#     plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, marker='X')
    
#     # X축, Y축 숨기기
#     plt.gca().set_xticks([])
#     plt.gca().set_yticks([])

#     # 배경 없애기 (투명하게 설정)
#     plt.gca().set_facecolor('none')
    
#     # 테두리 없애기
#     plt.gca().spines['top'].set_visible(False)
#     plt.gca().spines['right'].set_visible(False)
#     plt.gca().spines['left'].set_visible(False)
#     plt.gca().spines['bottom'].set_visible(False)

#     plt.show()