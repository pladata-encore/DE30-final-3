import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

# 모델 파일 불러오기
tier_to_load = 'Gold'  # 사용하려는 티어를 지정하세요.
model_filename = f"kmeans_model_tier_{tier_to_load}.pkl"

with open(model_filename, 'rb') as file:
    saved_model = pickle.load(file)
    
kmeans_model = saved_model['kmeans_model']
scaler = saved_model['scaler']
pca = saved_model['pca']
max_distances = saved_model['max_distances']

# 새로운 데이터 입력 (예제 데이터)
new_data = {
    'kills': [5, 7],
    'knockdowns': [3, 4],
    'assists': [1, 2],
    'total_damage': [800.0, 1500.0],
    'total_shot': [200, 100],
    'hit_count': [50, 62],
    'head_shot': [10, 20]
}

df_new = pd.DataFrame(new_data)

# 명중률과 헤드샷 명중률 계산
df_new['hit_rate'] = df_new['hit_count'] / df_new['total_shot'] * 100
df_new['headshot_rate'] = df_new['head_shot'] / df_new['total_shot'] * 100

# 저장된 Scaler와 PCA 모델을 사용하여 새로운 데이터에 동일한 전처리 적용
scaled_features = scaler.transform(df_new[["hit_rate", "kills", "knockdowns", "assists", "total_damage", "headshot_rate", "total_shot"]])
pca_features = pca.transform(scaled_features)
df_new['pca_one'] = pca_features[:, 0]
df_new['pca_two'] = pca_features[:, 1]

# 클러스터 예측
df_new['cluster'] = kmeans_model.predict(df_new[['pca_one', 'pca_two']])

# 클러스터 중심과 새로운 데이터 포인트 사이의 거리 계산
centers = kmeans_model.cluster_centers_
df_new['distance_to_center'] = df_new.apply(
    lambda row: np.linalg.norm([row['pca_one'], row['pca_two']] - centers[int(row['cluster'])]),
    axis=1
)

# 새로운 데이터가 이상치인지 판단
df_new['is_outlier'] = df_new.apply(
    lambda row: row['distance_to_center'] > max_distances[int(row['cluster'])],
    axis=1
)

# 결과 출력
print(df_new[['cluster', 'distance_to_center', 'is_outlier']])

# 시각화
plt.figure(figsize=(10, 7))
sns.scatterplot(x='pca_one', y='pca_two', hue='cluster', data=df_new, palette='viridis', s=100)

# 클러스터 중심
plt.scatter(centers[:, 0], centers[:, 1], color='blue', marker='X', s=200, label='Cluster Centers')

# 이상치 포인트
outliers = df_new[df_new['is_outlier']]
plt.scatter(outliers['pca_one'], outliers['pca_two'], color='red', label='Outliers', s=150)

# 각 클러스터의 최대 거리 원 그리기
for cluster_id, max_dist in max_distances.items():
    center = centers[cluster_id]
    circle = plt.Circle(center, max_dist, color='black', fill=False, linewidth=2)
    plt.gca().add_artist(circle)

plt.title(f'Outlier Detection for New Data in Tier {tier_to_load}')
plt.legend()
plt.show()
