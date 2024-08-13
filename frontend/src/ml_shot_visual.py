import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def shot_cluster_graph(response):
    # 데이터를 변수에 저장
    centers = response["result"]["centers"]
    cluster_number = response["result"]["cluster"]
    distance_to_center = response["result"]["distance_to_center"]
    max_distances = response["result"]["max_distances"]
    user_x = response["result"]["pca_one"]
    user_y = response["result"]["pca_two"]
    is_outlier = response['result']['is_outlier']

    # 시각화 크기 조절 및 설정
    fig, ax = plt.subplots(figsize=(6, 6))  # 그래프 크기를 6x6 인치로 설정

    # 색상 리스트 (클러스터의 수에 따라 필요하면 확장 가능)
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    # 클러스터 중심점을 그리고 원을 표시
    for i, center in enumerate(centers):
        color = colors[i % len(colors)]  # 색상 순환
        circle = plt.Circle(center, max_distances[str(i)], color=color, alpha=0.2, edgecolor=color, linestyle='--')
        ax.add_artist(circle)
        ax.plot(center[0], center[1], 'o', color=color, label=f'Cluster {i} Center')  # 클러스터 중심점

    # 사용자의 위치를 표시
    ax.plot(user_x, user_y, 'rx', markersize=10, label='User')

    # 그래프 설정
    ax.set_title(f'Cluster Visualization with User Position (Cluster {cluster_number})')
    ax.set_xlabel('PCA One')
    ax.set_ylabel('PCA Two')
    ax.legend()

    # x, y 좌표값 동일하게 맞춤 및 축 범위 고정
    ax.set_aspect('equal', 'box')
    ax.set_xlim(-10, 10)  # x축 범위 설정
    ax.set_ylim(-10, 10)  # y축 범위 설정

    # 그래프를 출력
    st.pyplot(fig)
    st.write(f"Nearest cluster center of this player: {cluster_number}")
    st.write(f"Distance from center: {distance_to_center}")
    st.write(f"Is Outlier?: {is_outlier}")