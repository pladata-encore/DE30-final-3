import streamlit as st
import base64

st.set_page_config(layout="wide") # 화면 구성 wide

# base64로 인코딩된 이미지를 반환하는 함수
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 페이지 배경 이미지를 설정하는 함수
def set_background(png_file):
    bin_str = get_base64(png_file)
    css = f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), 
                    url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .title {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 50px; /* 상단에서 간격 조정 */
        margin-bottom: 10px; /* 아래쪽 간격 조정 */
        color: black;
        font-size: 5rem;
        font-weight: bold;
    }}
    .content {{
        display: grid;
        justify-content: center;
        align-items: center;
        height: 80vh;
        color: black;
        font-size: 2rem;
        font-weight: bold;
    }}
    .centered {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 55vh; /* 컨텐츠가 중앙에 위치하도록 조정 */
        flex-direction: column;
        margin: 5px; /* 요소들 간의 간격 추가 */
        color: black;
        font-size: 10rem;
        font-weight: bold;
    }}
    .page-margin {{
        margin: 100px; /* 페이지 전체의 여백 조정 */
    }}
    .custom-container {{
        padding-right: 50%; /* 양쪽에 50%의 패딩을 추가하여 간격을 확보 */
        padding-left : 50%;
    }}
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)