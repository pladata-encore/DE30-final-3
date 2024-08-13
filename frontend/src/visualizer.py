import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString, Point
import streamlit as st
import numpy as np
from scipy.stats import norm
from math import pi


bg_black = '#4f4f4f'
bg_orange = '#e46c0b'
bg_yellow = '#ffc000'

def log_map(map_id, data):
    global bg_black, bg_orange, bg_yellow
    initial_path = "/home/ec2-user/streamlit/StreamlitFE/"
    low_res = "heatmap_low_images/"
    map_name = 'Erangel_Main.png'

    if map_id == "Desert_Main":
        map_name =  "Miramar_Main.png"
    elif map_id == "Erangel_Main":
        map_name =  "Erangel_Main.png"
    elif map_id == "Baltic_Main":
        map_name =  "Erangel_Main.png"    
    elif map_id == "Savage_Main":
        map_name =  "Sanhok_Main.png"
    elif map_id == "Kiki_Main":
        map_name =  "Deston_Main.png"
    elif map_id == "Tiger_Main":
        map_name =  "Taego_Main.png"
    elif map_id == "Summerland_Main":
        map_name =  "Karakin_Main.png"
    elif map_id == "DihorOtok_Main":
        map_name =  "Vikendi_Main.png"
    elif map_id == "Chimera_Main":
        map_name =  "Paramo_Main.png"
    elif map_id == "Neon_Main":
        map_name =  "Rondo_Main.png"     
    elif map_id == "Heaven_Main":
        map_name =  "Haven_Main.png"
    elif map_id == "Range_Main":
        map_name =  "Camp_Jackal_Main.png"               
    else:
        map_name == map_id + ".png"

    file_path = initial_path + low_res + map_name

    # 지도 이미지 로드
    map_image = plt.imread(file_path)

    # 지도 그리기
    fig, ax = plt.subplots(figsize=(4, 4))  # 사이즈를 4x4로 설정

    # 지도 이미지 표시
    ax.imshow(map_image, extent=[0, 819200, 0, 819200])  # PUBG 맵 크기 설정 (예: 8192 x 8192)

    # xy_location 데이터를 사용해 좌표 리스트 생성
    xy_location_list = [[item['location_x'], item['location_y']] for item in data['xy_location']]

    # y축 좌표 반전
    xy_location_list = [[x, 819200 - y] for x, y in xy_location_list]

    # Point 객체 생성
    points = [Point(x, y) for x, y in xy_location_list]

    # GeoDataFrame 생성
    gdf_points = gpd.GeoDataFrame(geometry=points)

    # 점들을 표시 (점들을 이어주지 않음)
    gdf_points.plot(ax=ax, marker='o', color='orange', markersize=2, zorder=3)  # 마커를 주황색으로 설정

    # 배경을 투명하게 설정
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # x축, y축, 타이틀 제거
    ax.axis('off')

    # Streamlit에서 플롯을 표시
    st.pyplot(fig)

def create_pie_chart(player_stats):
    global bg_black, bg_orange, bg_yellow
    labels = '1st', 'Top10','lose'
    key_wave = player_stats['body']['ranked_stats']['squad']
    win = round(key_wave['wins']/key_wave['play_count'],1)
    top10 = round(key_wave['top10s']/key_wave['play_count'],1)
    total = round((key_wave['play_count']-key_wave['wins']-key_wave['top10s'])/key_wave['play_count'],1)
    if total < 0 :
        total = 0
    sizes = [win,top10,total]
    colors = [bg_black, bg_orange, bg_yellow]
    # colors = ['#4f4f4f', '#e46c0b', '#ffc000']
    explode = (0.2, 0.1 , 0.1)  # explode 1st slice

    fig, ax = plt.subplots(figsize=(4, 4))
    fig.patch.set_facecolor('none')  # 파이 차트 전체 배경 투명하게 설정
    ax.pie(sizes, explode=explode, labels=labels, colors=colors,
           autopct='%1.1f%%', shadow=True, startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    return fig

def main_radar_chart(player_stats):
    global bg_black, bg_orange, bg_yellow
    labels = np.array(['kills', 'deaths', 'assists', 'kda', 'avg_rank'])
    
    k1 = player_stats['body']['ranked_stats']
    k2 = player_stats['body']['statistics']
    
    radar_data = []
    
    # Helper function to calculate stats and add to radar_data if valid
    def add_to_radar(mode, mode_key, label_prefix):
        if mode_key in k1 and mode_key in k2:
            stats = [
                round(calculate_score(k1[mode_key]['kills']/k1[mode_key]['play_count'], k2[mode_key]['kills_avg'], k2[mode_key]['kills_std']),1),
                100-round(calculate_score(k1[mode_key]['deaths']/k1[mode_key]['play_count'], k2[mode_key]['deaths_avg'], k2[mode_key]['deaths_std']),1),
                round(calculate_score(k1[mode_key]['assists']/k1[mode_key]['play_count'], k2[mode_key]['assists_avg'], k2[mode_key]['assists_std']),1),
                round(calculate_score(k1[mode_key]['kda'], k2[mode_key]['kda_avg'], k2[mode_key]['kda_std']),1),
                100-round(calculate_score(k1[mode_key]['avg_rank'], k2[mode_key]['avg_rank_avg'], k2[mode_key]['avg_rank_std']),1)
            ]
            
            if all(stat is not None for stat in stats):  # Ensure all stats are valid
                radar_data.append({
                    'label': f"{label_prefix.upper()}",
                    'stats': np.round(stats, 1)
                })

    # Add radar data for each mode
    add_to_radar('solo', 'solo', 'solo')
    add_to_radar('solo-fpp', 'solo-fpp', 'solo-fpp')
    add_to_radar('squad', 'squad', 'squad')
    add_to_radar('squad-fpp', 'squad-fpp', 'squad-fpp')
    
    # Create radar chart if there is valid data
    if not radar_data:
        return None  # No valid data to display

    fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    # Set up the radar chart
    ax.set_ylim(0, 100)
    ax.set_yticks([])
    ax.set_xticks([])  # 기본 xticks 제거
    ax.set_theta_offset(np.pi / 2)

    # Plot background grid
    for r in [20, 40, 60, 80, 100]:
        grid_angles = angles[:-1] + [angles[0]]
        grid_values = [r] * len(grid_angles)
        ax.plot(grid_angles, grid_values, color='gray', linewidth=1, linestyle='--')

    for angle in angles[:-1]:
        ax.plot([angle, angle], [0, 100], color='gray', linewidth=1)
    
    # Plot each radar chart
    for data in radar_data:
        stats = np.concatenate((data['stats'], [data['stats'][0]]))
        ax.fill(angles, stats, color=bg_orange, alpha=0.25)
        ax.plot(angles, stats, color=bg_orange, linewidth=2, label=data['label'])
        
        for i, (angle, stat) in enumerate(zip(angles, stats)):
            ax.text(angle, stat, str(stat), horizontalalignment='center', size=12, color=bg_black)

    # 각 축의 레이블을 표시
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=bg_black, size=12)

    # 범례 설정 (투명한 배경)
    legend = ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1), frameon=False)

    # 프레임을 오각형으로 설정
    ax.spines['polar'].set_visible(False)

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    ax.patch.set_facecolor(bg_black)

    return fig

def calculate_score(value, avg, std):
    global bg_black, bg_orange, bg_yellow
    if avg is None or std is None or value is None:
        return 0  # 기본 값 또는 무시하는 값을 설정할 수 있음
    z_score = (value - avg) / std
    percentile = norm.cdf(z_score) * 100
    return np.clip(percentile, 0, 100)

def match_radar_chart(match_data):
    global bg_black, bg_orange, bg_yellow
    labels = np.array(['호전성', '생존력', '유틸성', '전투력', '저격능력'])
    k1 = match_data['match_data']
    k2 = match_data['match_user_data']

    belligerence_score = k2['belligerence']
    belligerence_avg = k1['belligerence_avg']
    belligerence_std = k1['belligerence_std']

    viability_score = k2['viability']
    viability_avg = k1['viability_avg']
    viability_std = k1['viability_std']

    utility_score = k2['utility']
    utility_avg = k1['utility_avg']
    utility_std = k1['utility_std']

    combat_score = k2['viability']
    combat_avg = k1['combat_avg']
    combat_std = k1['combat_std']

    sniping_score = k2['sniping']
    sniping_avg = k1['sniping_avg']
    sniping_std = k1['sniping_std']

    stats = [
        round(calculate_score(belligerence_score,belligerence_avg,belligerence_std),1),
        round(calculate_score(viability_score,viability_avg,viability_std),1),
        round(calculate_score(utility_score,utility_avg,utility_std),1),
        round(calculate_score(combat_score,combat_avg,combat_std),1),
        round(calculate_score(sniping_score,sniping_avg,sniping_std),1)
    ]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats = np.concatenate((stats, [stats[0]]))
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))

    # 오각형 배경 그리기
    ax.set_ylim(0, 100)
    ax.set_yticks([])
    ax.set_xticks([])  # 기본 xticks 제거

    # 각도를 π/2(90도)만큼 회전시켜 오각형이 똑바로 나오도록 설정
    ax.set_theta_offset(pi / 2)

    # 그리드를 오각형으로 그리기
    for r in [20, 40, 60, 80, 100]:
        grid_angles = angles[:-1] + [angles[0]]
        grid_values = [r] * len(grid_angles)
        ax.plot(grid_angles, grid_values, color='gray', linewidth=1, linestyle='--')
    
    for angle in angles[:-1]:
        ax.plot([angle, angle], [0, 100], color='gray', linewidth=1)

    # 데이터 그리기
    ax.fill(angles, stats, color=bg_orange, alpha=0.25)
    ax.plot(angles, stats, color=bg_orange, linewidth=2)

    # x축 레이블 설정
    for i, angle in enumerate(angles[:-1]):
        ax.text(angle, 135, labels[i], horizontalalignment='center', size=12, color=bg_black)

    # 각 축마다 값을 표시
    for i, (angle, label, stat) in enumerate(zip(angles, labels, stats)):
        ax.text(angle, stat + 10, str(stat), horizontalalignment='center', size=12, color=bg_black)

        # 프레임을 오각형으로 설정
    ax.spines['polar'].set_visible(False)
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(1)
        spine.set_linestyle('--')

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    ax.patch.set_facecolor(bg_black)  # 차트 배경 색상 설정
    fig.patch.set_facecolor(bg_black)
    return fig


# def main_radar_chart(player_stats):
#     global bg_black, bg_orange, bg_yellow
#     labels = np.array(['kills', 'deaths', 'assists', 'kda', 'avg_rank'])
    
#     k1 = player_stats['body']['ranked_stats']
#     if 'solo' in k1:
#         solo_kills = k1['solo']['kills']
#         solo_deaths = k1['solo']['death']
#         solo_assists = k1['solo']['assists']
#         solo_kda = k1['solo']['kda']
#         solo_avg_rank = k1['solo']['avg_rank']
#     else:
#         pass
#     if 'solo-fpp' in k1:
#         solo_fpp_kills = k1['solo-fpp']['kills']
#         solo_fpp_deaths = k1['solo-fpp']['death']
#         solo_fpp_assists = k1['solo-fpp']['assists']
#         solo_fpp_kda = k1['solo-fpp']['kda']
#         solo_fpp_avg_rank = k1['solo-fpp']['avg_rank']
#     else:
#         pass
#     if 'squad' in k1:
#         squad_kills = k1['squad']['kills']
#         squad_deaths = k1['squad']['death']
#         squad_assists = k1['squad']['assists']
#         squad_kda = k1['squad']['kda']
#         squad_avg_rank = k1['squad']['avg_rank']
#     else:
#         pass        
#     if 'squad-fpp' in k1:
#         squad_fpp_kills = k1['squad-fpp']['kills']
#         squad_fpp_deaths = k1['squad-fpp']['death']
#         squad_fpp_assists = k1['squad-fpp']['assists']
#         squad_fpp_kda = k1['squad-fpp']['kda']
#         squad_fpp_avg_rank = k1['sosquadlo-fpp']['avg_rank']
#     else:
#         pass

#     k2 = player_stats['body']['statistics']
#     if 'solo' in k1:
#         solo_kills_avg = k2['solo']['kills_avg']
#         solo_kills_std = k2['solo']['kills_std']
#         solo_deaths_avg = k2['solo']['deaths_avg']
#         solo_deaths_std = k2['solo']['deaths_std']
#         solo_assists_avg = k2['solo']['assists_avg']
#         solo_assists_std = k2['solo']['assists_std']
#         solo_kda_avg = k2['solo']['kda_avg']
#         solo_kda_std = k2['solo']['kda_std']
#         solo_avg_rank_avg = k2['solo']['avg_rank_avg']
#         solo_avg_rank_std = k2['solo']['avg_rank_std']
#     else:
#         pass
#     if 'solo-fpp' in k1:
#         solo_fpp_kills_avg = k2['solo-fpp']['kills_avg']
#         solo_fpp_kills_std = k2['solo-fpp']['kills_std']
#         solo_fpp_deaths_avg = k2['solo-fpp']['deaths_avg']
#         solo_fpp_deaths_std = k2['solo-fpp']['deaths_std']
#         solo_fpp_assists_avg = k2['solo-fpp']['assists_avg']
#         solo_fpp_assists_std = k2['solo-fpp']['assists_std']
#         solo_fpp_kda_avg = k2['solo-fpp']['kda_avg']
#         solo_fpp_kda_std = k2['solo-fpp']['kda_std']
#         solo_fpp_avg_rank_avg = k2['solo-fpp']['avg_rank_avg']
#         solo_fpp_avg_rank_std = k2['solo-fpp']['avg_rank_std']
#     else:
#         pass
#     if 'squad' in k1:
#         squad_kills_avg = k2['squad']['kills_avg']
#         squad_kills_std = k2['squad']['kills_std']
#         squad_deaths_avg = k2['squad']['deaths_avg']
#         squad_deaths_std = k2['squad']['deaths_std']
#         squad_assists_avg = k2['squad']['assists_avg']
#         squad_assists_std = k2['squad']['assists_std']
#         squad_kda_avg = k2['squad']['kda_avg']
#         squad_kda_std = k2['squad']['kda_std']
#         squad_avg_rank_avg = k2['squad']['avg_rank_avg']
#         squad_avg_rank_std = k2['squad']['avg_rank_std']
#     else:
#         pass
#     if 'squad-fpp' in k1:
#         squad_fpp_kills_avg = k2['squad-fpp']['kills_avg']
#         squad_fpp_kills_std = k2['squad-fpp']['kills_std']
#         squad_fpp_deaths_avg = k2['squad-fpp']['deaths_avg']
#         squad_fpp_deaths_std = k2['squad-fpp']['deaths_std']
#         squad_fpp_assists_avg = k2['squad-fpp']['assists_avg']
#         squad_fpp_assists_std = k2['squad-fpp']['assists_std']
#         squad_fpp_kda_avg = k2['squad-fpp']['kda_avg']
#         squad_fpp_kda_std = k2['squad-fpp']['kda_std']
#         squad_fpp_avg_rank_avg = k2['squad-fpp']['avg_rank_avg']
#         squad_fpp_avg_rank_std = k2['squad-fpp']['avg_rank_std']
#     else:
#         pass

#     stats = [
#         round(calculate_score(solo_kills,solo_kills_avg,solo_kills_std),1),
#         round(calculate_score(solo_deaths,solo_deaths_avg,solo_deaths_std),1),
#         round(calculate_score(solo_assists,solo_assists_avg,solo_assists_std),1),
#         round(calculate_score(solo_kda,solo_kda_avg,solo_kda_std),1),
#         round(calculate_score(solo_avg_rank,solo_avg_rank_avg,solo_avg_rank_std),1)
#     ]

#     angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
#     stats = np.concatenate((stats, [stats[0]]))
#     angles += angles[:1]

#     fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))

#     # 오각형 배경 그리기
#     ax.set_ylim(0, 100)
#     ax.set_yticks([])
#     ax.set_xticks([])  # 기본 xticks 제거

#     # 각도를 π/2(90도)만큼 회전시켜 오각형이 똑바로 나오도록 설정
#     ax.set_theta_offset(pi / 2)

#     # 그리드를 오각형으로 그리기
#     for r in [20, 40, 60, 80, 100]:
#         grid_angles = angles[:-1] + [angles[0]]
#         grid_values = [r] * len(grid_angles)
#         ax.plot(grid_angles, grid_values, color='gray', linewidth=1, linestyle='--')
    
#     for angle in angles[:-1]:
#         ax.plot([angle, angle], [0, 100], color='gray', linewidth=1)

#     # 데이터 그리기
#     ax.fill(angles, stats, color=bg_orange, alpha=0.25)
#     ax.plot(angles, stats, color=bg_orange, linewidth=2)

#     # x축 레이블 설정
#     for i, angle in enumerate(angles[:-1]):
#         ax.text(angle, 125, labels[i], horizontalalignment='center', size=12, color=bg_black)

#     # 각 축마다 값을 표시
#     for i, (angle, label, stat) in enumerate(zip(angles, labels, stats)):
#         ax.text(angle, stat + 10, str(stat), horizontalalignment='center', size=12, color=bg_black)

#         # 프레임을 오각형으로 설정
#     ax.spines['polar'].set_visible(False)
#     for spine in ax.spines.values():
#         spine.set_edgecolor('gray')
#         spine.set_linewidth(1)
#         spine.set_linestyle('--')

#     fig.patch.set_alpha(0)
#     ax.patch.set_alpha(0)
#     ax.patch.set_facecolor(bg_black)  # 차트 배경 색상 설정

#     return fig