import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 레이아웃 및 디자인 정밀 조정
# ======================================================
st.markdown("""
<style>
    /* 상단 여백 최소화 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    [data-testid="stAppViewContainer"], .main-container, .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    .main-container {
        max-width: 100% !important;
        margin: auto;
        font-family: 'Segoe UI', sans-serif;
    }

    /* 헤더 - 여백 최소화 및 폰트 크기 확대 */
    .header {
        display: flex;
        align-items: center;
        border-bottom: 5px solid black;
        padding-bottom: 5px;
        margin-bottom: 15px;
        margin-top: -30px; /* 위쪽 여백 바짝 붙임 */
    }
    .header img { height: 50px; margin-right: 15px; }
    .title { 
        font-size: 52px; /* 폰트 사이즈 확대 */
        font-weight: 900; 
        line-height: 1;
    }

    .section-title { font-size: 18px; font-weight: 900; margin-top: 15px; margin-bottom: 10px; }

    /* 결과 박스 - 가로 배치용 스타일 */
    .result-box-container {
        display: flex;
        align-items: center;
        width: 100%;
        gap: 5%; /* 박스 사이 여백 5% */
    }
    
    .result-box-value {
        width: 50% !important; /* 폭 50% */
        font-size: 26px;
        font-weight: 900;
        padding: 15px 5px;
        background: #ffe5cc;
        border: 2px solid black;
        text-align: center;
        color: black !important;
        display: inline-block;
    }

    .status-box {
        width: 45% !important; /* 폭 45% */
        font-size: 26px;
        font-weight: 900;
        padding: 15px 5px;
        border: 2px solid black;
        text-align: center;
        display: inline-block;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }

    /* 버튼 스타일 - 검정 테두리 및 5% 간격 대응 */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 65px !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        background-color: #f0f0f0 !important;
        color: black !important;
        border: 3px solid black !important;
        border-radius: 0px !important;
    }

    /* 입력창 정렬 */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    /* 푸터 로고 정렬 */
    .footer {
        display: flex;
        align-items: center;
        margin-top: 30px;
        border-top: 1px solid #eeeeee;
        padding-top: 15px;
    }
    .footer-logo-img {
        height: 35px;
        margin-right: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 로직 및 세션 상태
# ======================================================
EFFICIENCY = {
    "SAW":  {"AWS": 1.0, "ISO": 1.0},
    "GMAW": {"AWS": 1.0, "ISO": 0.8},
    "FCAW": {"AWS": 1.0, "ISO": 0.8},
    "SMAW": {"AWS": 1.0, "ISO": 0.8},
}

if "history" not in st.session_state:
    st.session_state.history = []