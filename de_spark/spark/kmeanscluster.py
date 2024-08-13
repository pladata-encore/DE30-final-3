from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pandas as pd

# kmeans 클러스터링 함수 (sklearn 사용)
def perform_kmeans_clustering(df, features_cols, k_range=(2, 11), seed=1, sample_fraction=0.1):
    

    # 최적의 k 값 찾기
    silhouette_scores = []
    for k in range(*k_range):
        kmeans = KMeans(n_clusters=k, random_state=seed)
        kmeans.fit(df[features_cols])
        labels = kmeans.labels_
        silhouette = silhouette_score(df[features_cols], labels)
        silhouette_scores.append((k, silhouette))

    if silhouette_scores:
        best_k, best_score = max(silhouette_scores, key=lambda x: x[1])
    else:
        best_k = 4  # 기본값

    # 최종 클러스터링
    kmeans = KMeans(n_clusters=best_k, random_state=seed)
    df['cluster'] = kmeans.fit_predict(df[features_cols])


    return df

##### when you use pyspark.ml

# from pyspark.ml.evaluation import ClusteringEvaluator
# from pyspark.ml.clustering import KMeans
# from pyspark.sql.functions import col
# # from sklearn.cluster import KMeans
# # from sklearn.metrics import silhouette_score

# # kmeans 클러스터링 함수
# def perform_kmeans_clustering(df, features_col="features", k_range=(2, 11), seed=1):

#     # 최적의 k 값 찾기
#     silhouette_scores = []
#     for k in range(*k_range):
#         kmeans = KMeans().setK(k).setSeed(seed).setFeaturesCol(features_col)
#         model = kmeans.fit(df)
#         predictions = model.transform(df)
#         evaluator = ClusteringEvaluator()
#         silhouette = evaluator.evaluate(predictions)
#         silhouette_scores.append((k, silhouette))

#     if silhouette_scores:
#         best_k, best_score = max(silhouette_scores, key=lambda x: x[1])
#     else:
#         best_k = 4  # 기본값

#     # 최종 클러스터링
#     kmeans = KMeans().setK(best_k).setSeed(seed).setFeaturesCol(features_col)
#     model = kmeans.fit(df)
#     predictions = model.transform(df)

#     return predictions.withColumn("cluster", col("prediction")).drop("prediction")
