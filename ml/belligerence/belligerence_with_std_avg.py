import pymysql
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import numpy as np

# RDS 연결 설정
db_config = {
    'host': 'de30-final-3-db-mysql.cve6gqgcih9t.ap-northeast-2.rds.amazonaws.com',
    'user': 'admin',
    'password': '72767276',
    'database': 'de30_final_3',
}

# RDS 연결
conn = pymysql.connect(**db_config)

# SQL 쿼리 작성 및 실행
query = """
SELECT account_id, match_id, total_shots, landed_location_x, landed_location_y, map_id
FROM match_details
"""
df = pd.read_sql(query, conn)

# 데이터 전처리
df.dropna(inplace=True)
df['landed_location_x'] = df['landed_location_x'].astype(float)
df['landed_location_y'] = df['landed_location_y'].astype(float)

# y 값 변환 (map_id에 따라 절대값을 씌운 후 각 맵마다 다른 값을 사용)
map_y_offsets = {
    'Desert_Main': 816000,
    'Baltic_Main': 816000,
    'DihorOtok_Main': 816000,
    'Erangel_Main': 816000,
    'Tiger_Main': 816000,
    'Neon_Main': 816000,
    'Savage_Main': 408000,
    'Chimera_Main': 306000,
    'Summerland_Main': 204000,
    'Heaven_Main': 102000
}

df['landed_location_y'] = df.apply(
    lambda row: map_y_offsets.get(row['map_id'], 816000) - abs(row['landed_location_y']), axis=1
)

# 매치별로 클러스터링 및 호전성 계산
results = []
for match_id, group in df.groupby('match_id'):
    xy_values = group[['landed_location_x', 'landed_location_y']].values
    
    # 스케일링
    scaler = StandardScaler()
    xy_values_scaled = scaler.fit_transform(xy_values)
    
    # 데이터 포인트 수 확인
    n_samples = len(xy_values_scaled)
    if n_samples < 4:
        print(f"Match ID: {match_id} has too few data points to cluster. Skipping...")
        continue
    
    max_clusters = min(10, n_samples)  # 데이터 포인트 수보다 클러스터 수가 많아지지 않도록 설정
    
    # 최적의 클러스터 수 찾기
    silhouette_scores = []
    for k in range(4, max_clusters + 1):  # 최소 4개에서 최대 클러스터 개수
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(xy_values_scaled)
        labels = kmeans.labels_
        
        # 레이블이 1개 이하인 경우 silhouette score를 계산하지 않음
        if len(set(labels)) > 1:
            silhouette_avg = silhouette_score(xy_values_scaled, labels)
            silhouette_scores.append((k, silhouette_avg))
    
    if not silhouette_scores:
        print(f"Match ID: {match_id} could not produce a valid cluster. Skipping...")
        continue
    
    # 최적의 클러스터 수로 클러스터링 수행
    optimal_k = max(silhouette_scores, key=lambda x: x[1])[0]
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    group['cluster'] = kmeans.fit_predict(xy_values_scaled)
    
    # 클러스터 점수 계산 및 호전성 점수 계산
    cluster_counts = group['cluster'].value_counts().to_dict()
    group['cluster_score'] = group['cluster'].map(cluster_counts)
    group['belligerence'] = group['cluster_score'] * 20 + group['total_shots']
    
    # 매치별 평균 호전성 및 표준편차 계산
    match_mean_belligerence = group['belligerence'].mean()
    match_std_belligerence = group['belligerence'].std()
    
    # 각 클러스터에 속한 account_id 수 출력
    cluster_distribution = group['cluster'].value_counts().to_dict()
    cluster_info = ', '.join([f'cluster{cluster}: {count}' for cluster, count in cluster_distribution.items()])
    
    # 결과 출력
    print(f"Match ID: {match_id}, Optimal number of clusters: {optimal_k}")
    print(f"  - Cluster Distribution: {cluster_info}")
    print(f"  - Unique clustered accounts: {group['account_id'].nunique()}")
    print(f"  - Match Mean Belligerence: {match_mean_belligerence:.2f}")
    print(f"  - Match Belligerence Std Dev: {match_std_belligerence:.2f}\n")
    
    results.append(group)

# 최종 결과 데이터프레임
df_result = pd.concat(results)

# RDS 연결 종료
conn.close()
