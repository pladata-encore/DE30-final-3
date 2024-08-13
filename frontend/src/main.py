import streamlit as st
from matplotlib import pyplot as plt
from matplotlib import font_manager
import matplotlib.font_manager as font_manager
from submit import page1to2, page2toml, switch_to_heatmap, page2toshot_ml
import requests
from visualizer import log_map, create_pie_chart, main_radar_chart, match_radar_chart
from ml_speed_visual import ml_speed_main
from heatmap import load_data, process_and_cluster_map_data
from PIL import Image
import seaborn as sns
from ml_shot_visual import shot_cluster_graph

# 폰트 경로 설정
font_path_ttf = "/usr/share/fonts/D2CodingAll/D2CodingBold-Ver1.3.2-20180524-ligature.ttf"
font_prop = font_manager.FontProperties(fname=font_path_ttf)
# 폰트를 추가하여 사용
font_manager.fontManager.addfont(font_path_ttf)
# 폰트 적용
plt.rcParams['font.family'] = font_prop.get_name()

def page1(switch_page):
    # 상단에 배경 이미지를 설정한 헤더 추가
    st.markdown('<div class="centered">SSB.GG</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 5])
        with col1:
            st.selectbox(" ", ["kakao", "steam"], key="platform")
        with col2:
            st.text_input(" ", placeholder="닉네임을 입력하세요", key="nickname", on_change=page1to2)
        st.markdown('</div>', unsafe_allow_html=True)

def page2(switch_page):
    st.markdown(
    """
    <style>
    /* 사이드바 너비 조절 */
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 200px;  /* 원하는 너비로 변경 */
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 200px;  /* 원하는 너비로 변경 */
        margin-left: -200px;  /* 숨겨진 상태에서의 너비 */
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Main Page", "Heatmap"])

    if page == "Heatmap":
        switch_page("heatmap_page")
        switch_to_heatmap()
        return  
    st.markdown("""
        <style>
        .custom-header {
            background-color: #333333;
            padding: 20px;  /* 상단바의 패딩을 20px로 설정 */
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            color: #FFA500;
            height: 100px;
        }
        .content {
            padding-top: 10px; /* 상단바 높이만큼 패딩 추가 */
        }
        .custom-header .title {
            color : #FFA500;
            font-size: 60px;
            font-weight: bold;
            padding-bottom : 40px;
            margin-right : 40px;
            margin-left: 350px;  /* 왼쪽 여백을 350px로 설정하여 오른쪽으로 이동 */
        }
        .custom-header .menu {
            display: flex;
            align-items: center;
        }
        .custom-header .menu a {
            color: #FFA500;
            text-decoration: none;
            margin-left: auto;
            font-size: 20px;
            margin-right: 150px;
        }
        .search-bar {
            display: flex;
            align-items: center;
        }
        .search-bar input {
            font-size: 10px;
            padding: 5px;
            margin-right: 0px;
        }
        .search-bar button {
            font-size: 15px; /* 버튼의 글자 크기 조절 */
            color: black;
        }
        .custom-container {
            border: 2px solid #FFA500; /* 테두리 색상 설정 */
            border-radius: 10px; /* 테두리 모서리 둥글게 설정 */
            padding: 10px; /* 내부 여백 추가 */
            margin-bottom: 20px; /* 컨테이너 간 간격 추가 */
            background-color: rgba(255, 255, 255, 0.1); /* 반투명 배경 설정 */
            width: 100%;
        }
        .custom-image {
            width: 200px; /* 원하는 너비로 설정 */
            height: auto; /* 비율을 유지하면서 높이를 자동으로 조절 */
        }
        .custom-row {
            display: flex;
            align-items: stretch;
            justify-content: space-between;
            height: 500px; /* 줄일 높이 설정 */
        }
        .custom-col {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .custom-col img, .custom-col div, .custom-col canvas {
            max-width: 100%;
            max-height: 100%;
        }
        </style>
        <script>
        function submitForm() {
            const platform = document.getElementById('search-platform').value;
            const nickname = document.getElementById('search-nickname').value;
            console.log(platform)
            if (platform && nickname) {
                const queryParams = new URLSearchParams({ platform: platform, nickname: nickname });
                const newUrl = `${window.location.pathname}?${queryParams.toString()}`;
                window.history.pushState({}, '', newUrl);
                window.location.reload();
            }
        }
        
        function getQueryParams() {
            const urlParams = new URLSearchParams(window.location.search);
            
            return {
                platform: urlParams.get('platform')[0],
                nickname: urlParams.get('nickname')
            };
        }
        
        document.addEventListener("DOMContentLoaded", function() {
            const params = getQueryParams();
           
            if (params.platform && params.nickname) {
                fetch("/set_session_state", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(params)
                }).then(response => {
                    if (response.ok) {
                        
                        window.location.reload();
                    }
                });
            }
        });
        </script>
        """, unsafe_allow_html=True)

    # 상단바
    st.markdown("""
    <div class="custom-header">
        <div class="title">SBB.GG</div>
        <div class="menu">
            <div class="search-bar">
                <div class="custom-container">
                    <form onsubmit="submitForm(); return false;">
                        <label for="platform1">플랫폼:</label>
                        <select name="platform" id="search-platform">
                            <option value="kakao">kakao</option>
                            <option value="steam">steam</option>
                        </select>
                        <label for="nickname">닉네임:</label>
                        <input type="text" name="nickname" id="search-nickname" placeholder="enter_player_name" />
                        <button type="submit">search</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 쿼리 파라미터 받아오기2
    query_params = st.query_params
    platform1 = query_params.get('search-platform', [''])[0]
    nickname1 = query_params.get('search-nickname', [''])[0]

    if platform1 and nickname1:
        # print(platform1)
        # print(nickname1)
        st.session_state['platform'] = platform1
        st.session_state['nickname'] = nickname1
        page1to2()

    if 'page' not in st.session_state:
        st.session_state.page = 'page1'

    if "player_stats" in st.session_state:
        player_stats = st.session_state.player_stats
        # st.write(player_stats)  # 플레이어 통계 데이터를 화면에 출력
        account_id = player_stats.get('body',{})['account_id']
        shard = player_stats.get('body',{})['shard']
    else:
        st.write("No player_stats available. Please go back and enter player information.")

    if "ranked_match" in st.session_state:
        ranked_match = st.session_state.ranked_match
        # st.write(ranked_match)  # 플레이어 통계 데이터를 화면에 출력
    else:
        st.write("No ranked_match available. Please go back and enter player information.")
    
    # # 컨텐츠를 상단바 아래로 이동시키기 위한 패딩 추가
    # st.markdown('<div class="content">', unsafe_allow_html=True)

    with st.container():
        # 플레이어 정보와 이미지 그룹화
        # st.markdown('<div class="custom-row">', unsafe_allow_html=True)
        # st.markdown('<div class="custom-col">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])

        # with col1:
        #     st.markdown('<div class="custom-col">', unsafe_allow_html=True)
        #     st.image("https://cdn-icons-png.flaticon.com/512/10568/10568151.png", caption="", use_column_width=True)
        #     st.markdown('</div>', unsafe_allow_html=True)

        with col1:
            key_wave = player_stats['body']['ranked_stats']['squad']
            st.markdown(f"""
                    <div class="custom-col">
                        <h2>{key_wave['latest_nickname']}</h2>
                        <p>Best Rank Point : {key_wave['best_rp']}</p>
                        <p>Current Rank Point : {key_wave['current_rp']}</p>
                        <p>Best Tier : {key_wave['best_tier']} {key_wave['best_subtier']}</p>
                        <p>Current Tier : {key_wave['current_tier']} {key_wave['current_subtier']}</p>
                        <p>Game Play Counts : {key_wave['play_count']}</p>
                        <p>Win : {key_wave['wins']}</p>
                        <p>Top 10s : {key_wave['top10s']}</p>
                        <p>KDA : {key_wave['kda']}</p>
                        <p>Kills : {key_wave['kills']}</p>
                        <p>Knockdowns : {key_wave['knockdowns']}</p>
                        <p>Assists : {key_wave['assists']}</p>
                        <p>Deaths : {key_wave['deaths']}</p>
                        <p>Total Damage : {key_wave["total_damage"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="custom-col">', unsafe_allow_html=True)
            st.pyplot(main_radar_chart(player_stats))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="custom-col">', unsafe_allow_html=True)
            st.pyplot(create_pie_chart(player_stats))
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if ranked_match:
        rank_filtered_data = ranked_match.get('body',[])
        for i in range(1, len(rank_filtered_data)+1):
            post_rank_filtered_data = {
                "account_id": account_id,
                "match_id": rank_filtered_data[i-1],
                "shard": shard
            }
            # st.write(post_rank_filtered_data)
            get_process_url = f"http://10.11.10.125:5000/match/process/{shard}/{account_id}/{rank_filtered_data[i-1]}"
            # st.write(post_process_url)
            # post_process_response = requests.post(post_process_url, json=post_rank_filtered_data)
            get_process_response = requests.get(get_process_url)

            if get_process_response.status_code == 200:
                session_key = f"match_data_{i}"
                st.session_state[session_key] = get_process_response.json()
                # st.write(f"Match data POST request sent successfully! Session state key: {session_key}")
                # st.write(f"match_id : {rank_filtered_data[i-1]}")

                get_speed_url = f"http://10.11.10.125:5000/match/overwatch/speed/{shard}/{account_id}/{rank_filtered_data[i-1]}"
                
                # st.write(post_speed_url)
                # post_speed_response = requests.post(post_speed_url, json = post_rank_filtered_data)
                get_speed_response = requests.get(get_speed_url)

                if get_speed_response.status_code == 200:
                    speed_session_key = f"speed_data_{i}"
                    st.session_state[speed_session_key] = get_speed_response.json()
                    # st.write(st.session_state[f"speed_data_{i}"])
                    # st.write(f"Speed data POST request sent successfully! Session state key: {speed_session_key}")
                else:
                    st.write(f"Failed to send GET speed request for match_id: {rank_filtered_data[i-1]}")
                    st.write(f"status_code : {get_speed_response.status_code}")
                    st.write(f"request body : ", post_rank_filtered_data)

                get_shot_url = f"http://10.11.10.125:5000/match/overwatch/shot/{shard}/{account_id}/{rank_filtered_data[i-1]}"
                get_shot_response = requests.get(get_shot_url)

                if get_shot_response.status_code == 200:
                    shot_session_key = f"shot_data_{i}"
                    st.session_state[shot_session_key] = get_shot_response.json()
                    
                    # st.write(get_shot_response.json())
                else:
                    st.write(f"Failed to send GET shot request for match_id: {rank_filtered_data[i-1]}")
                    st.write(f"status_code : {get_shot_response.status_code}")
                    st.write(f"request body : ", post_rank_filtered_data)               
            else:
                st.write(f"Failed to send GET process request for match_id: {rank_filtered_data[i-1]}")
                st.write(f"status_code : {get_process_response.status_code}")
                st.write(f"request body : ", post_rank_filtered_data)

            # break
    match_data_list = []
    for i in range(1,6):
        try:
            if f"match_data_{i}" in st.session_state:
                match_data_list.append(st.session_state[f"match_data_{i}"])
                # st.write(st.session_state[f"match_data_{i}"])
        except:
            print("no data available")
            pass

    # 최근 플레이 로그
    count=1
    st.session_state['button_number'] = 0
    for i in match_data_list:
        k1 = i['match_data']
        k2 = i['match_user_data']
        map_id = k1['map_id']
        expander_label = f"{k1['mode_id'].upper()}&nbsp;&nbsp;&nbsp;&nbsp;RANK : {k2['ranking']}\tKILL : {k2['kills']}\tDAMAGE : {round(k2['damage_dealt'])}\tSURVIVAL TIME : {k2['lifetime']//60}:{k2['lifetime']%60}"

        with st.expander(expander_label, expanded=False):
            st.markdown(
                f"""
                <div style="font-size:18px; font-weight:bold; color:#333;">
                    {k1['mode_id'].upper()}
                    RANK : {k2['ranking']} &nbsp;&nbsp;
                    KILL : {k2['kills']} &nbsp;&nbsp;
                    DAMAGE : {round(k2['damage_dealt'])} &nbsp;&nbsp;
                    SURVIVAL TIME : {k2['lifetime']//60}:{k2['lifetime']%60}
                </div>
                """, 
                unsafe_allow_html=True
            )
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    bg_black = '#4f4f4f'
                    bg_orange = '#e46c0b'
                    bg_yellow = '#ffc000'
                    st.markdown(
                        """
                        <style>
                        .container {
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                        }
                        .header-box {
                            width: 85%;  /* 헤더 박스 너비 설정 */
                            background-color: '#4f4f4f';  /* 박스 배경 색상 설정 */
                            padding: 5px 10px;  /* 박스 내부 여백 설정 */
                            margin: 5px 0;  /* 박스 간격 설정 */
                            border-radius: 10px;
                            border: 1px solid #ddd;
                            box-sizing: border-box;  /* 테두리와 패딩 포함한 크기 계산 */
                            color: #ffc000;  /* 글자 색상 설정 */
                            text-align: center;
                        }
                        .custom-box-container {
                            display: flex;
                            flex-wrap: wrap;
                            justify-content: space-around;
                            gap: 5px;
                            width: 90%;
                        }
                        .custom-box {
                            width: 90%;  /* 박스 너비 설정 */
                            background-color: '#4f4f4f';  /* 박스 배경 색상 설정 */
                            padding: 5px 10px;  /* 박스 내부 여백 설정 */
                            margin: 5px;  /* 박스 간격 설정 */
                            border-radius: 10px;
                            border: 1px solid #ddd;
                            box-sizing: border-box;  /* 테두리와 패딩 포함한 크기 계산 */
                            color: #4f4f4f;  /* 글자 색상 설정 */
                            text-align: center;
                        }
                        .custom-box p {
                            margin: 5px 0;
                        }
                        </style>
                        """, unsafe_allow_html=True
                    )

                    st.markdown(
                        f"""
                        <div class="container">
                            <div class="header-box">
                                <h2>{k2['ranking']}</h2>
                            </div>
                            <div class="custom-box-container" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                                <div class="custom-box">
                                    <p>Move Distance</p>
                                    <p>{round(k2['total_distance'],2)}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Kill</p>
                                    <p>{k2['kills']}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Assists</p>
                                    <p>{k2['assists']}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Revives</p>
                                    <p>{k2['revives']}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Longest Kill Distance</p>
                                    <p>{round(k2['longest_kill_dist'],3)}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Fire Accuracy</p>
                                    <p>{round(k2['accuracy'],2)}%</p>
                                </div>
                                <div class="custom-box">
                                    <p>Heal Count</p>
                                    <p>{k2['heal_count']}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Survive Time</p>
                                    <p>{k2['lifetime']}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Damage</p>
                                    <p>{round(k2['damage_dealt'],2)}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Knockdown</p>
                                    <p>{k2['knockdowns']}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Boost Count</p>
                                    <p>{k2['boost_count']}</p>
                                </div>
                                <div class="custom-box">
                                    <p>Throw Count</p>
                                    <p>{k2['throw_count']}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                with col2:
                    st.pyplot(match_radar_chart(i))  # 레이더 차트 추가
                with col3:
                    # 맵 로그 표시
                    xy_data = st.session_state.get(f"speed_data_{count}")
                    if xy_data:
                        log_map(map_id, xy_data)
                    
                    # 버튼이 눌리면 `page2toml` 함수가 실행되고, 페이지가 전환됨
                    if st.button("Go To Speed ML Page", key=f"go_to_speed_page_{count}"):
                        st.session_state['button_number'] = count
                        page2toml()  # 함수 실행
                    elif st.button("Go To Shot ML Page", key=f"go_to_shot_page_{count}"):
                        st.session_state['button_number'] = count
                        page2toshot_ml()  # 함수 실행
                    count += 1

def ml_page(switch_page):
    # 상단바 스타일 설정
    st.markdown("""
        <style>
        .custom-header {
            background-color: #333333;
            padding: 20px;  /* 상단바의 패딩을 20px로 설정 */
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            color: #FFA500;
            height: 100px;
        }
        .content {
            padding-top: 20px; /* 상단바 높이만큼 패딩 추가 */
        }
        .custom-header .title {
            color : #FFA500;
            font-size: 60px;
            font-weight: bold;
            padding-bottom : 40px;
            margin-right : 40px;
            margin-left: 350px;  /* 왼쪽 여백을 350px로 설정하여 오른쪽으로 이동 */
        }
        .custom-header .menu {
            display: flex;
            align-items: center;
        }
        .custom-header .menu a {
            color: #FFA500;
            text-decoration: none;
            margin-left: auto;
            font-size: 20px;
            margin-right: 150px;
        }
        .search-bar {
            display: flex;
            align-items: center;
        }
        .search-bar input {
            font-size: 10px;
            padding: 5px;
            margin-right: 0px;
        }
        .search-bar button {
            font-size: 15px; /* 버튼의 글자 크기 조절 */
            color: black;
        }
        .custom-container {
            border: 2px solid #FFA500; /* 테두리 색상 설정 */
            border-radius: 10px; /* 테두리 모서리 둥글게 설정 */
            padding: 10px; /* 내부 여백 추가 */
            margin-bottom: 20px; /* 컨테이너 간 간격 추가 */
            background-color: rgba(255, 255, 255, 0.1); /* 반투명 배경 설정 */
            width: 100%;
        }
        .custom-image {
            width: 200px; /* 원하는 너비로 설정 */
            height: auto; /* 비율을 유지하면서 높이를 자동으로 조절 */
        }
        .custom-row {
            display: flex;
            align-items: stretch;
            justify-content: space-between;
            height: 500px; /* 줄일 높이 설정 */
        }
        .custom-col {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .custom-col img, .custom-col div, .custom-col canvas {
            max-width: 100%;
            max-height: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # 상단바
    st.markdown("""
    <div class="custom-header">
        <div class="title">SBB.GG</div>
        <div class="menu">
            <div class="search-bar">
                <div class="custom-container">
                    <form onsubmit="submitForm(); return false;">
                        <label for="platform1">플랫폼:</label>
                        <select name="platform" id="search-platform">
                            <option value="kakao">kakao</option>
                            <option value="steam">steam</option>
                        </select>
                        <label for="nickname">닉네임:</label>
                        <input type="text" name="nickname" id="search-nickname" placeholder="enter_player_name" />
                        <button type="submit">search</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

        # 뒤로가기 버튼 추가
    if st.button("Back", key="back_button_from_ml"):
        switch_page("page2")  # page2로 이동

    # 페이지 전환 후 예측 결과 출력
    button_number = st.session_state.get('button_number', 0)
    if button_number != 0:
        predictions = st.session_state.get(f"speed_data_{button_number}", {}).get('predictions', [])
        if predictions:
            # st.write(predictions)
            ml_speed_main(predictions)
        else:
            st.write("No predictions data available.")


def shot_ml_page(switch_page):
    # 상단바 스타일 설정
    st.markdown("""
        <style>
        .custom-header {
            background-color: #333333;
            padding: 20px;  /* 상단바의 패딩을 20px로 설정 */
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            color: #FFA500;
            height: 100px;
        }
        .content {
            padding-top: 20px; /* 상단바 높이만큼 패딩 추가 */
            margin-left: 50px; /* 왼쪽 공백 추가 */
            margin-right: 50px; /* 오른쪽 공백 추가 */
        }
        .custom-header .title {
            color : #FFA500;
            font-size: 60px;
            font-weight: bold;
            padding-bottom : 40px;
            margin-right : 40px;
            margin-left: 350px;  /* 왼쪽 여백을 350px로 설정하여 오른쪽으로 이동 */
        }
        .custom-header .menu {
            display: flex;
            align-items: center;
        }
        .custom-header .menu a {
            color: #FFA500;
            text-decoration: none;
            margin-left: auto;
            font-size: 20px;
            margin-right: 150px;
        }
        .search-bar {
            display: flex;
            align-items: center;
        }
        .search-bar input {
            font-size: 10px;
            padding: 5px;
            margin-right: 0px;
        }
        .search-bar button {
            font-size: 15px; /* 버튼의 글자 크기 조절 */
            color: black;
        }
        .custom-container {
            border: 2px solid #FFA500; /* 테두리 색상 설정 */
            border-radius: 10px; /* 테두리 모서리 둥글게 설정 */
            padding: 10px; /* 내부 여백 추가 */
            margin-bottom: 20px; /* 컨테이너 간 간격 추가 */
            background-color: rgba(255, 255, 255, 0.1); /* 반투명 배경 설정 */
            width: 100%;
        }
        .custom-image {
            width: 200px; /* 원하는 너비로 설정 */
            height: auto; /* 비율을 유지하면서 높이를 자동으로 조절 */
        }
        .custom-row {
            display: flex;
            align-items: stretch;
            justify-content: space-between;
            height: 500px; /* 줄일 높이 설정 */
        }
        .custom-col {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .custom-col img, .custom-col div, .custom-col canvas {
            max-width: 100%;
            max-height: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # 상단바
    st.markdown("""
    <div class="custom-header">
        <div class="title">SBB.GG</div>
        <div class="menu">
            <div class="search-bar">
                <div class="custom-container">
                    <form onsubmit="submitForm(); return false;">
                        <label for="platform1">플랫폼:</label>
                        <select name="platform" id="search-platform">
                            <option value="kakao">kakao</option>
                            <option value="steam">steam</option>
                        </select>
                        <label for="nickname">닉네임:</label>
                        <input type="text" name="nickname" id="search-nickname" placeholder="enter_player_name" />
                        <button type="submit">search</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 뒤로가기 버튼 추가
    if st.button("Back", key="back_button_from_shot_ml"):
        switch_page("page2")  # page2로 이동

    # 페이지 전환 후 예측 결과 출력
    button_number = st.session_state.get('button_number', 0)
    if button_number != 0:
        # 예시 함수, 실제 사용하려는 함수로 대체
        shot_cluster_graph(st.session_state[f"shot_data_{button_number}"])
        # st.write("Displaying data...")
def heatmap_page(switch_page):
    st.markdown(
    """
    <style>
    /* 사이드바 너비 조절 */
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 200px;  /* 원하는 너비로 변경 */
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 200px;  /* 원하는 너비로 변경 */
        margin-left: -200px;  /* 숨겨진 상태에서의 너비 */
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    # 사이드바에 "뒤로가기" 버튼을 추가
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Main Page","Heatmap"])

    if page == "Main Page":
        switch_page("page2")
        # page1to2()
        return
    # 상단바 스타일 설정
    st.markdown("""
        <style>
        .custom-header {
            background-color: #333333;
            padding: 20px;  /* 상단바의 패딩을 20px로 설정 */
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            color: #FFA500;
            height: 100px;
        }
        .content {
            padding-top: 20px; /* 상단바 높이만큼 패딩 추가 */
        }
        .custom-header .title {
            color : #FFA500;
            font-size: 60px;
            font-weight: bold;
            padding-bottom : 40px;
            margin-right : 40px;
            margin-left: 350px;  /* 왼쪽 여백을 350px로 설정하여 오른쪽으로 이동 */
        }
        .custom-header .menu {
            display: flex;
            align-items: center;
        }
        .custom-header .menu a {
            color: #FFA500;
            text-decoration: none;
            margin-left: auto;
            font-size: 20px;
            margin-right: 150px;
        }
        .search-bar {
            display: flex;
            align-items: center;
        }
        .search-bar input {
            font-size: 10px;
            padding: 5px;
            margin-right: 0px;
        }
        .search-bar button {
            font-size: 15px; /* 버튼의 글자 크기 조절 */
            color: black;
        }
        .custom-container {
            border: 2px solid #FFA500; /* 테두리 색상 설정 */
            border-radius: 10px; /* 테두리 모서리 둥글게 설정 */
            padding: 10px; /* 내부 여백 추가 */
            margin-bottom: 20px; /* 컨테이너 간 간격 추가 */
            background-color: rgba(255, 255, 255, 0.1); /* 반투명 배경 설정 */
            width: 100%;
        }
        .custom-image {
            width: 200px; /* 원하는 너비로 설정 */
            height: auto; /* 비율을 유지하면서 높이를 자동으로 조절 */
        }
        .custom-row {
            display: flex;
            align-items: stretch;
            justify-content: space-between;
            height: 500px; /* 줄일 높이 설정 */
        }
        .custom-col {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .custom-col img, .custom-col div, .custom-col canvas {
            max-width: 100%;
            max-height: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # 상단바
    st.markdown("""
    <div class="custom-header">
        <div class="title">SBB.GG</div>
        <div class="menu">
            <div class="search-bar">
                <div class="custom-container">
                    <form onsubmit="submitForm(); return false;">
                        <label for="platform1">플랫폼:</label>
                        <select name="platform" id="search-platform">
                            <option value="kakao">kakao</option>
                            <option value="steam">steam</option>
                        </select>
                        <label for="nickname">닉네임:</label>
                        <input type="text" name="nickname" id="search-nickname" placeholder="enter_player_name" />
                        <button type="submit">search</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        
    # 절대 경로로 변환된 배경 이미지 경로
    base_url = "/home/ec2-user/streamlit/StreamlitFE/heatmap_low_images/"
    map_background_images = {
        'Desert_Main': base_url + "Miramar_Main.png",
        'Baltic_Main': base_url + "Erangel_Main.png",
        'DihorOtok_Main': base_url + "Vikendi_Main.png",
        'Tiger_Main': base_url + "Taego_Main.png",
        'Neon_Main': base_url + "Rondo_Main.png",
        'Kiki_Main': base_url + "Deston_Main.png",
        'Savage_Main': base_url + "Sanhok_Main.png",
        'Chimera_Main': base_url + "Paramo_Main.png",
        'Summerland_Main': base_url + "Karakin_Main.png",
        'Heaven_Main': base_url + "Haven_Main.png"
    }

    map_y_offsets = {
        'Desert_Main': 816000,
        'Baltic_Main': 816000,
        'DihorOtok_Main': 816000,
        # 'Erangel_Main': 816000,
        'Tiger_Main': 816000,
        'Neon_Main': 816000,
        # 'Kiki_Main': 816000,
        'Savage_Main': 408000
        # 'Chimera_Main': 306000,
        # 'Summerland_Main': 204000,
        # 'Heaven_Main': 102000
    }

    map_extents = {
        'Desert_Main': [0, 816000, 0, 816000],
        'Baltic_Main': [0, 816000, 0, 816000],
        'DihorOtok_Main': [0, 816000, 0, 816000],
        # 'Erangel_Main': [0, 816000, 0, 816000],
        'Tiger_Main': [0, 816000, 0, 816000],
        'Neon_Main': [0, 816000, 0, 816000],
        # 'Kiki_Main': [0, 816000, 0, 816000],
        'Savage_Main': [0, 408000, 0, 408000]
        # 'Chimera_Main': [0, 306000, 0, 306000],
        # 'Summerland_Main': [0, 204000, 0, 204000],
        # 'Heaven_Main': [0, 102000, 0, 102000]
    }

    # 사이드바에 맵 이름으로 버튼 생성
    st.sidebar.title("Map Selection")
    selected_map = st.sidebar.radio("Choose a map", list(map_y_offsets.keys()))
    if selected_map == "Desert_Main":
        renamed_map = "Miramar"
    elif selected_map == "Baltic_Main":
        renamed_map = "Erangel"
    elif selected_map == "DihorOtok_Main":
        renamed_map = "Vikendi"
    elif selected_map == "Tiger_Main":
        renamed_map = "Taego"
    elif selected_map == "Neon_Main":
        renamed_map = "Rondo"
    elif selected_map == "Savage_Main":
        renamed_map = "Sanhok"
    # 페이지 전환 후 히트맵 출력
    if selected_map:
        matches_df, match_user_df = load_data()  # 필요에 따라 데이터를 로드하거나 이 과정은 생략할 수 있음
        st.title(f"Landing Heatmap : {renamed_map}")

        group, centers = process_and_cluster_map_data(selected_map, match_user_df, matches_df, map_y_offsets)

        plt.figure(figsize=(5, 4))

        # 배경 이미지 로드
        if selected_map in map_background_images:
            img_path = map_background_images[selected_map]
            img = Image.open(img_path)
            if selected_map in map_extents:
                extent = map_extents[selected_map]
                # custom_extent = [extent[0], extent[1] * 1.1, extent[2], extent[3] * 1.1]  # 가로 및 세로 크기를 80%로 조정
                plt.imshow(img, extent=extent, aspect='auto')  # 배경 이미지의 투명도 설정

        # 히트맵 생성
        sns.kdeplot(
            x=group['landed_location_x'], 
            y=group['landed_location_y'], 
            fill=True, 
            cmap='viridis', 
            bw_adjust=0.5, 
            alpha=0.5, 
            thresh=0.1
        )  # 히트맵의 색상 및 투명도 설정
        # X축, Y축 레이블 제거
        plt.xlabel('')
        plt.ylabel('')

        # 상위 5개의 클러스터 강조
        top_clusters = group['cluster'].value_counts().head(5).index
        for cluster in top_clusters:
            cluster_center = centers[cluster]
            plt.scatter(cluster_center[0], cluster_center[1], c='yellow', s=200, edgecolors='black', label=f'Top Cluster {cluster}', marker='X')

        # X축, Y축 숨기기
        plt.gca().set_xticks([])
        plt.gca().set_yticks([])

        # 배경 없애기 (투명하게 설정)
        plt.gca().set_facecolor('none')

        # 테두리 없애기
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)

        # 제목 제거
        plt.gca().set_title("")

        # 범례 위치 조정 (필요에 따라 제거 가능)
        # plt.legend(loc='upper right', frameon=False)

        # 여백 제거
        plt.tight_layout(pad=0)
        
        # 저장할 때 여백 제거
        st.pyplot(plt, bbox_inches='tight', pad_inches=0)
        plt.close()