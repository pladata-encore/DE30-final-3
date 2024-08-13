import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sqlalchemy import create_engine
import pickle

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

# 모든 티어 리스트 (플래티넘과 다이아몬드, 마스터 포함)
tiers_to_process = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master']

# 각 티어별로 클러스터링 및 이상치 식별
for tier in tiers_to_process:
    if tier == 'Diamond':
        df_tier = df_selected[df_selected['current_tier'].isin(['Platinum', 'Diamond'])].copy()
    elif tier == 'Master':
        df_tier = df_selected[df_selected['current_tier'].isin(['Diamond', 'Master'])].copy()
    else:
        df_tier = df_selected[df_selected['current_tier'] == tier].copy()

    if not df_tier.empty:
        print(f"Processing Tier: {tier}")

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

            if len(np.unique(cluster_labels)) > 1:
                silhouette_avg = silhouette_score(df_tier[['pca_one', 'pca_two']], cluster_labels)
                silhouette_scores.append(silhouette_avg)
            else:
                silhouette_scores.append(-1)

        if max(silhouette_scores) != -1:
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
            max_distances = df_tier.groupby('cluster')['distance_to_center'].max().to_dict()
            df_tier['is_outlier'] = df_tier.apply(
                lambda row: row['distance_to_center'] > max_distances[row['cluster']],
                axis=1
            )

            # 이상치로 판별된 데이터 출력
            outliers = df_tier[df_tier['is_outlier']]
            print(f"\nOutliers in Tier {tier}:")
            print(outliers[['account_id', 'match_id', 'kills', 'knockdowns', 'assists', 'total_damage', 'total_shot', 'hit_count', 'head_shot', 'cluster', 'distance_to_center']])

            # 모델과 필요한 정보를 pkl 파일로 저장 (클러스터 중심점 포함)
            model_filename = f"kmeans_model_tier_{tier}.pkl"
            with open(model_filename, 'wb') as file:
                pickle.dump({
                    'kmeans_model': kmeans,
                    'scaler': scaler,
                    'pca': pca,
                    'max_distances': max_distances,
                    'centers': centers  # 클러스터 중심점을 추가로 저장
                }, file)
            print(f"Model for Tier {tier} saved as {model_filename}")
