import streamlit as st # type: ignore
import requests
import builtins

def page1to2():
    st.session_state.page = "page2"
    platform = st.session_state.get('platform', '')
    nickname = st.session_state.get('nickname', '')
    if not isinstance(platform, str) and not isinstance(nickname, str) :
        platform = platform[0]
        nickname = nickname[0]
    # st.write(platform,nickname)
    # Flask로 GET 요청 보내기
    backend_url = f"http://10.11.10.125:5000/user/{platform}/{nickname}"
    response = requests.get(backend_url)
    if response.status_code == 200:
        # st.write(response.json())
        st.session_state.player_stats = response.json()  # 응답 데이터를 JSON 형식으로 파싱하여 세션 상태에 저장
        # st.write("Data sent successfully!")

        # 필요한 데이터 파싱
        data = st.session_state.player_stats.get('body', {})
        account_id = data.get('account_id',"")
        match_ids = data.get('matches', [])
        shard = data.get('shard')
        n = 5  # 필요한 값 설정

        post_data = {
            "n": n,
            "shard": shard,
            "match_ids": match_ids
        }

        # POST 요청 보내기
        post_url = "http://10.11.10.125:5000/match/filterrankedmatches"  # 실제 POST 요청을 보낼 엔드포인트 URL
        post_response = requests.post(post_url, json=post_data)

        if post_response.status_code == 200:
            st.session_state.ranked_match = post_response.json()
        else:
            # st.write("Failed to POST ranked_match.")
            pass
    else:
        st.write("Failed to get player_stats.")
        st.write(response.status_code)
        pass

def page2toml():
    st.session_state.page = "ml_page"  # 페이지를 "ml_page"로 전환
    st.experimental_rerun()  # 페이지를 새로고침하여 전환된 페이지를 렌더링

def switch_to_heatmap():
# 페이지 전환 체크 및 화면 전환
    st.session_state.page = "heatmap_page" 
    st.experimental_rerun()
    # st.experimental_set_query_params(page="heatmap_page" )

def page2toshot_ml():
    st.session_state.page = "shot_ml_page"  # 페이지를 "ml_page"로 전환
    st.experimental_rerun()  # 페이지를 새로고침하여 전환된 페이지를 렌더링