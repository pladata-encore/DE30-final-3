import os
import pandas as pd
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# RDS 연결 설정
db_config = {
    'host': 'de30-final-3-db-mysql.cve6gqgcih9t.ap-northeast-2.rds.amazonaws.com',
    'user': 'admin',
    'password': '72767276',
    'database': 'de30_final_3',
}

# SQLAlchemy 엔진 생성
engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

# 데이터 쿼리
matches_query = "SELECT season_id, match_id, map_id FROM matches"
match_user_query = """
    SELECT match_id, landed_location_x, landed_location_y 
    FROM match_user
    WHERE landed_location_x IS NOT NULL AND landed_location_y IS NOT NULL
"""

# 데이터 프레임으로 로드
matches_df = pd.read_sql(matches_query, engine)
match_user_df = pd.read_sql(match_user_query, engine)

# 숫자형 변환
match_user_df['landed_location_x'] = pd.to_numeric(match_user_df['landed_location_x'], errors='coerce')
match_user_df['landed_location_y'] = pd.to_numeric(match_user_df['landed_location_y'], errors='coerce')

# 특정 조건에 맞는 데이터 필터링 (x가 0이고 y는 816000 또는 408000인 데이터 제거)
match_user_df = match_user_df[~((match_user_df['landed_location_x'] == 0) & (match_user_df['landed_location_y'].isin([816000, 408000])))]

# 각 맵의 Y 좌표 오프셋 정의 및 맵 크기 (extent) 설정
map_y_offsets = {
    'Desert_Main': 816000,
    'Baltic_Main': 816000,
    'DihorOtok_Main': 816000,
    'Erangel_Main': 816000,
    'Tiger_Main': 816000,
    'Neon_Main': 816000,
    'Kiki_Main': 816000,
    'Savage_Main': 408000,
    'Chimera_Main': 306000,
    'Summerland_Main': 204000,
    'Heaven_Main': 102000
}

map_extents = {
    'Desert_Main': [0, 816000, 0, 816000],
    'Baltic_Main': [0, 816000, 0, 816000],
    'DihorOtok_Main': [0, 816000, 0, 816000],
    'Erangel_Main': [0, 816000, 0, 816000],
    'Tiger_Main': [0, 816000, 0, 816000],
    'Neon_Main': [0, 816000, 0, 816000],
    'Kiki_Main': [0, 816000, 0, 816000],
    'Savage_Main': [0, 408000, 0, 408000],
    'Chimera_Main': [0, 306000, 0, 306000],
    'Summerland_Main': [0, 204000, 0, 204000],
    'Heaven_Main': [0, 102000, 0, 102000]
}

# 배경 이미지 경로 설정
map_background_images = {
    'Desert_Main': "/home/ec2-user/minsung/jupyter_files/images/Miramar_Main_High_Res.png",
    'Baltic_Main': "/home/ec2-user/minsung/jupyter_files/images/Erangel_Main_High_Res.png",
    'DihorOtok_Main': "/home/ec2-user/minsung/jupyter_files/images/Vikendi_Main_High_Res.png",
    'Tiger_Main': "/home/ec2-user/minsung/jupyter_files/images/Taego_Main_High_Res.png",
    'Neon_Main': "/home/ec2-user/minsung/jupyter_files/images/Rondo_Main_High_Res.png",
    'Kiki_Main': "/home/ec2-user/minsung/jupyter_files/images/Deston_Main_High_Res.png",
    'Savage_Main': "/home/ec2-user/minsung/jupyter_files/images/Sanhok_Main_High_Res.png",
    'Chimera_Main': "/home/ec2-user/minsung/jupyter_files/images/Paramo_Main_High_Res.png",
    'Summerland_Main': "/home/ec2-user/minsung/jupyter_files/images/Karakin_Main_High_Res.png",
    'Heaven_Main': "/home/ec2-user/minsung/jupyter_files/images/Haven_Main_High_Res.png"
}

# 절대 경로로 변환
for key, path in map_background_images.items():
    map_background_images[key] = os.path.abspath(path)

# 데이터 처리 및 클러스터링
results = []

for map_name, group in match_user_df.groupby(match_user_df['match_id'].map(matches_df.set_index('match_id')['map_id'])):
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

    # 클러스터링 결과 저장
    results.append((map_name, group, centers))

# 시각화 및 결과 출력
for map_name, group, centers in results:
    plt.figure(figsize=(10, 8))

    # 배경 이미지 로드
    if map_name in map_background_images:
        img_path = map_background_images[map_name]
        img = Image.open(img_path)
        if map_name in map_extents:
            extent = map_extents[map_name]
            plt.imshow(img, extent=extent, aspect='auto')  # 배경 이미지의 투명도 설정

    # 히트맵 생성
    sns.kdeplot(
        x=group['landed_location_x'], 
        y=group['landed_location_y'], 
        fill=True, 
        cmap='viridis', 
        bw_adjust=0.5, 
        alpha=0.5, 
        thresh=0.1
    )  # 히트맵의 색상 및 투명도 설정
    
    # 상위 5개의 클러스터 강조
    top_clusters = group['cluster'].value_counts().head(5).index
    for cluster in top_clusters:
        cluster_center = centers[cluster]
        plt.scatter(cluster_center[0], cluster_center[1], c='yellow', s=200, edgecolors='black', label=f'Top Cluster {cluster}', marker='X')

    plt.title(f"Landing Heatmap - Map {map_name}")
    plt.xlabel('landed_location_x')
    plt.ylabel('landed_location_y')
    plt.legend()
    plt.show()
