from submit import page1to2
import streamlit as st
from background import set_background
from main import page1,page2,ml_page, heatmap_page, shot_ml_page

#세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'page1'

# 페이지 전환 함수
def switch_page(page):
    st.session_state.page = page
    st.experimental_rerun()
if __name__ == '__main__':
    # Streamlit 상단 바와 메뉴 숨기기
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # 이미지 파일 경로 설정
    image_path = '/home/ec2-user/streamlit/StreamlitFE/static/images/battleground1.png'
    # 배경 이미지 설정 함수 호출
    set_background(image_path)
    # 현재 페이지에 따라 다른 UI를 표시합니다.

    query_params = st.query_params.get_all
    platform = st.query_params.get_all('platform')
    nickname = st.query_params.get_all('nickname')

    if platform and nickname:
        print(platform)
        print(nickname)
        st.session_state['platform'] = platform
        st.session_state['nickname'] = nickname
        page1to2()

    if 'page' not in st.session_state:
        st.session_state.page = 'page1'

    if st.session_state.page == 'page1':
        page1(switch_page)
    elif st.session_state.page == 'page2':
        page2(switch_page)
    elif st.session_state.page == 'ml_page':
        ml_page(switch_page)
    elif st.session_state.page == 'heatmap_page':
        heatmap_page(switch_page)
    elif st.session_state.page == 'shot_ml_page':
        shot_ml_page(switch_page)
