# 속도 분포 시각화 (히스토그램)
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np


# 속도 분포 시각화 (히스토그램)
def plot_speed_distribution(data):
    plt.figure(figsize=(10, 6))

    # 'Normal' 상태의 km_per_h 데이터 추출 및 시각화
    sns.histplot(
        [item['km_per_h'] for item in data if item['status'] == 'Normal'], 
        color='blue', label='Normal', kde=True, stat="density"
    )
    
    # 'Outlier' 상태의 km_per_h 데이터 추출 및 시각화
    sns.histplot(
        [item['km_per_h'] for item in data if item['status'] != 'Normal'], 
        color='red', label='Outlier', kde=True, stat="density"
    )
    
    plt.title('Speed Distribution')
    plt.xlabel('Speed (km/h)')
    plt.ylabel('Density')
    plt.legend()
    # 그래프를 접었다 폈다 할 수 있는 expander 추가
    with st.expander("Show/Hide Speed Distribution Visualization"):
        st.pyplot(plt)  # Streamlit에서 그래프 표시
    
    plt.close()


# 차량별 예측 결과 막대 그래프
def plot_vehicle_predictions(data):
    account_ids = list(set(item['account_id'] for item in data))
    
    # account_id 별로 normal과 outlier를 카운트
    normal_count = [sum((item['account_id'] == account_id) and (item['status'] == 'Normal') for item in data) for account_id in account_ids]
    anomaly_count = [sum((item['account_id'] == account_id) and (item['status'] != 'Normal') for item in data) for account_id in account_ids]

    x = np.arange(len(account_ids))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, normal_count, width, label='Normal')
    plt.bar(x + width/2, anomaly_count, width, label='Outlier')

    plt.xlabel('Account ID')
    plt.ylabel('Count')
    plt.title('Vehicle Predictions')
    plt.xticks(x, account_ids, rotation=45, ha='right')  # Account ID를 축에 표시
    # plt.legend()

    # 그래프를 접었다 폈다 할 수 있는 expander 추가
    with st.expander("Show/Hide Vehicle Predictions Graph"):
        st.pyplot(plt)  # Streamlit에서 그래프 표시
    
    plt.close()

def plot_speed_index_scatter(data):
    plt.figure(figsize=(10, 6))
    
    for idx, item in enumerate(data):
        color = 'blue' if item['status'] == 'Normal' else 'red'
        plt.scatter(idx, item['km_per_h'], color=color, label=item['account_id'])

    plt.title('Speed vs. Index')
    plt.xlabel('Index')
    plt.ylabel('Speed (km/h)')
    plt.legend(loc="upper right")
    # 그래프를 접었다 폈다 할 수 있는 expander 추가
    with st.expander("Show/Hide Speed-Time Scatter Plot"):
        st.pyplot(plt)  # Streamlit에서 그래프 표시
    
    plt.close()

def display_summary_table(data):
    summary_data = []
    for item in data:
        summary_data.append([item['account_id'], item['km_per_h'], item['status']])

    summary_df = pd.DataFrame(summary_data, columns=['Account ID', 'Speed (km/h)', 'Status'])

    # 테이블을 접었다 폈다 할 수 있는 expander 추가
    with st.expander("Show/Hide Summary Table"):
        st.table(summary_df)  # Streamlit에서 테이블 표시

# Streamlit 앱에서 사용할 예시 코드
def ml_speed_main(predictions):
    # st.write(predictions)
    # 각 함수 호출
    st.title("Speed Distribution Visualization")
    plot_speed_distribution(predictions)
    
    st.title("Vehicle Predictions") 
    plot_vehicle_predictions(predictions)
    
    st.title("Speed-Time Scatter Plot")
    plot_speed_index_scatter(predictions)
    
    st.title("Summary Table")
    display_summary_table(predictions)
