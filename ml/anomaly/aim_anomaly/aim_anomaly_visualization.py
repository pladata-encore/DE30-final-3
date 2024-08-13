import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sqlalchemy import create_engine

# MySQL 데이터베이스에 연결 설정
engine = create_engine("mysql+pymysql://admin:72767276@de30-final-3-db-mysql.cve6gqgcih9t.ap-northeast-2.rds.amazonaws.com/de30_final_3")

# 데이터 로드 (for_ml_user 테이블에서 데이터 가져오기)
query = """
SELECT account_id, match_id, current_tier, kills, knockdowns, assists, total_damage, total_shot, hit_count, head_shot 
FROM for_ml_user
"""
df_selected = pd.read_sql(query, engine)

# 필요한 추가 계산
df_selected['hit_rate'] = df_selected['hit_count'] / df_selected['total_shot'] * 100
df_selected['headshot_rate'] = df_selected['head_shot'] / df_selected['total_shot'] * 100

# 결측치 처리
df_selected = df_selected.dropna()

# 티어별로 그룹화
tiers = df_selected['current_tier'].unique()

for tier in tiers:
    print(f"Processing Tier: {tier}")
    df_tier = df_selected[df_selected['current_tier'] == tier]

    # 데이터 정규화
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df_tier[["hit_rate", "kills", "knockdowns", "assists", "total_damage", "headshot_rate", "total_shot"]])

    # PCA를 사용한 차원 축소 (예: 2차원으로 축소)
    pca = PCA(n_components=2)
    pca_features = pca.fit_transform(scaled_features)
    df_tier['pca_one'] = pca_features[:, 0]
    df_tier['pca_two'] = pca_features[:, 1]

    # 최적의 클러스터 수 찾기 (엘보우 기법과 실루엣 계수 사용)
    silhouette_scores = []
    k_values = range(2, 11)

    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(df_tier[['pca_one', 'pca_two']])
        cluster_labels = kmeans.labels_

        silhouette_avg = silhouette_score(df_tier[['pca_one', 'pca_two']], cluster_labels)
        silhouette_scores.append(silhouette_avg)

    # 최적의 k 결정 (실루엣 점수가 가장 높은 k)
    optimal_k = k_values[silhouette_scores.index(max(silhouette_scores))]

    # 최적의 k로 KMeans 모델 훈련
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    df_tier['cluster'] = kmeans.fit_predict(df_tier[['pca_one', 'pca_two']])

    # 클러스터 중심과 각 데이터 포인트 사이의 거리 계산
    centers = kmeans.cluster_centers_
    df_tier['distance_to_center'] = df_tier.apply(
        lambda row: np.linalg.norm([row['pca_one'], row['pca_two']] - centers[row['cluster']]),
        axis=1
    )

    # 각 클러스터의 중심과 가장 먼 거리를 이상치로 판단
    outliers = pd.DataFrame()
    for cluster in range(optimal_k):
        cluster_data = df_tier[df_tier['cluster'] == cluster]
        center = centers[cluster]
        distances = np.linalg.norm(cluster_data[['pca_one', 'pca_two']] - center, axis=1)
        max_distance = distances.max()
        
        # 가장 먼 거리에 해당하는 이상치 포인트 선택
        cluster_outliers = cluster_data[distances == max_distance]
        outliers = pd.concat([outliers, cluster_outliers])

    # 이상치로 판별된 데이터 출력
    print(f"\nOutliers in Tier {tier}:")
    print(outliers[['account_id', 'match_id', 'kills', 'knockdowns', 'assists', 'total_damage', 'total_shot', 'hit_count', 'head_shot', 'cluster', 'distance_to_center']])

    # 이상치 시각화
    plt.figure(figsize=(10, 7))
    sns.scatterplot(x='pca_one', y='pca_two', hue='cluster', data=df_tier, palette='viridis', s=100)
    plt.scatter(outliers['pca_one'], outliers['pca_two'], color='red', label='Outliers', s=150)
    plt.title(f'Outliers in KMeans Clustering for Tier {tier}')
    plt.legend()
    plt.show()
