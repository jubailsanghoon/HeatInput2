import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 화이트 테마 고정 및 모바일 최적화 (타이틀 및 주황색 선 적용)
# ======================================================
st.markdown("""
<style>
    [data-testid="stAppViewContainer"], .main-container, .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    h1, h2, h3, p, span, div, label, .stMarkdown {
        color: #000000 !important;
    }
    .main-container {
        max-width: 100% !important;
        margin: auto;
        font-family: 'Segoe UI', sans-serif;
        padding: 10px;
    }
    /* 헤더 영역 수정: 주황색 수평선 적용 */
    .header {
        display: flex;
        align-items: center;
        border-bottom: 5px solid #ff7f00; /* 검정에서 주황색(#ff7f00)으로 변경 */
        padding-bottom: 12px;
        margin-bottom: 15px;
    }
    .header img { height: 50px; margin-right: 15px; } /* 이미지 크기 소폭 상향 */
    
    /* 타이틀 폰트 크기 상향 */
    .title { 
        font-size: 32px; /* 22px에서 32px로 상향 */
        font-weight: 900; 
        letter-spacing: -1px;
    }
    
    .section-title { font-size: 16px; font-weight: 900; margin-top: 12px; margin-bottom: 8px; }
    .result-box {
        font-size: 24px;
        font-weight: 900;
        padding: 12px;
        background: #ffe5cc;
        border: 1px solid #cccccc;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 8px;
        color: black !important;
        box-shadow: none;
    }
    .pass, .fail {
        font-size: 24px;
        font-weight: 900;
        padding: 12px;
        border: 1px solid #cccccc;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: none;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }
    
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 60px !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        background-color: #f0f0f0 !important;
        color: black !important;
        border: 2px solid black !important;
        border-radius: 4px !important;
        margin-top: 5px;
    }
    input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
        gap: 0.5rem;
    }
    .k-info { font-size: 13px; color: #555 !important; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# [이후 로직은 동일하게 유지됩니다]

# 열효율(k) 테이블
EFFICIENCY = {
    "SAW":  {"AWS": 1.0, "ISO": 1.0},
    "GMAW": {"AWS": 1.0, "ISO": 0.8},
    "FCAW": {"AWS": 1.0, "ISO": 0.8},
    "SMAW": {"AWS": 1.0, "ISO": 0.8},
}

def validate_inputs(voltage, current, length, time_s):
    errors = []
    if voltage <= 0: errors.append("전압(Volt)은 0보다 커야 합니다.")
    if current <= 0: errors.append("전류(Amp)는 0보다 커야 합니다.")
    if length <= 0: errors.append("비드 길이(Len)는 0보다 커야 합니다.")
    if time_s <= 0: errors.append("시간(Time)은 0보다 커야 합니다.")
    return errors

def draw_input_row(label, value, key, step=0.1, fmt="%.1f"):
    r_cols = st.columns([1.5, 2])
    with r_cols[0]: st.markdown("**" + label + "**")
    with r_cols[1]: return st.number_input(label, value=value, step=step, format=fmt, key=key, label_visibility="collapsed")

if "history" not in st.session_state: st.session_state.history = []

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header (업데이트된 스타일 적용)
st.markdown(
    f'<div class="header">'
    f'<img src="