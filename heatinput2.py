import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 화이트 테마 및 디자인 포인트 적용
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
    .header { 
        display: flex; 
        align-items: center; 
        border-bottom: 5px solid #ff7f00; /* 주황색 포인트 수평선 */
        padding-bottom: 12px; 
        margin-bottom: 15px; 
    }
    .header img { height: 50px; margin-right: 15px; }
    .title { 
        font-size: 32px; /* 타이틀 폰트 크기 상향 */
        font-weight: 900; 
        letter-spacing: -1px;
    }
    .section-title { font-size: 16px; font-weight: 900; margin-top: 12px; margin-bottom: 8px; }
    .result-box { font-size: 24px; font-weight: 900; padding: 12px; background:#ffe5cc; border:2px solid black; text-align: center; margin-bottom: 8px; color: black !important; }
    .pass, .fail { font-size: 24px; font-weight: 900; padding: 12px; border: 2px solid black; text-align: center; margin-bottom: 12px; }
    .pass { background:#00cc44; color:white !important; }
    .fail { background:#ff7f00; color:white !important; }
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
    .k-info { font-size: 13px; color:#555 !important; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 열효율(k) 테이블
# ======================================================
EFFICIENCY = {
    "SAW":  {"AWS": 1.0, "ISO": 1.0},
    "GMAW": {"AWS": 1.0, "ISO": 0.8},
    "FCAW": {"AWS": 1.0, "ISO": 0.8},
    "SMAW": {"AWS": 1.0, "ISO": 0.8},
}

# ======================================================
# 입력값 유효성 검사 함수
# ======================================================
def validate_inputs(voltage, current, length, time_s):
    errors = []
    if voltage <= 0:   errors.append("전압(Volt)은 0보다 커야 합니다.")
    if current <= 0:   errors.append("전류(Amp)는 0보다 커야 합니다.")
    if length <= 0:    errors.append("비드 길이(Len)는 0보다 커야 합니다.")
    if time_s <= 0:    errors.append("시간(Time)은 0보다 커야 합니다.")
    return errors

# 입력 행 렌더링 헬퍼
def draw_input_row(label, value, key, step=0.1, fmt="%.1f"):
    r_cols = st.columns([1.5, 2])
    with r_cols[0]:
        st.markdown(f"**{label}**")
    with r_cols[1]:
        return st.number_input(label, value=value, step=step, format=fmt, key=key, label_visibility="collapsed")

# 세션 상태 초기화
if 'history' not in st.session_state:
    st.session_state.history = []

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ======================================================
# Header (주황색 선 & 큰 타이틀)
# ======================================================
st.markdown("""
<div class="header">
  <img src="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg">
  <div class="title">Heat Input Master</div>
</div>
""", unsafe_allow_html=True)

# 1. Standard & Process Selection
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS", "ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True, label_visibility="collapsed")

k = EFFICIENCY[process][standard]
st.markdown(f'<div class="k-info">🔧 Thermal Efficiency (k) = <b>{k}</b> | {standard} / {process}</div>', unsafe_allow_html=True)

# 2. WPS Range
st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
w_cols = st.columns([0.5, 1.5, 0.5, 1.5])
with w_cols[0]: st.markdown("**Min**")
with w_cols[1]: min_range = st.number_input("min", value=0.96, step=0.01, format="%.2f", label_visibility="collapsed")
with w_cols[2]: st.markdown("**Max**")
with w_cols[3]: max_range = st.number_input("max", value=2.50, step=0.01, format="%.2f", label_visibility="collapsed")

# 3. Input Parameters & Live Result
st.write("")
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    voltage = draw_input_row("Volt (V)", 30.0, "v")
    current = draw_input_row("Amp (A)", 300.0, "c")
    length  = draw_input_row("Len (mm)", 5.0,  "l")
    time_s  = draw_input_row("Time (s)", 1.0,  "t")

# [에러 수정 완료 구역]
errors = validate_inputs(voltage, current, length, time_s)

if not errors:
    HI = (k * voltage * current * time_s) / (length * 1000)
    status = "PASS" if min_range <= HI <= max_range else "FAIL" # <- 따옴표 닫기 완료!
else:
    HI = 0.0
    status = "FAIL"

with col_right:
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{round(HI, 3)} kJ/mm</div>', unsafe_allow_html=True)
    if errors:
        st.markdown('<div class="fail">INPUT ERR</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="{status.lower()}">{status}</div>', unsafe_allow_html=True)

# 4. Save & History
if st.button("Save Data"):
    if not errors:
        new_data = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Std": standard, "Prc": process, "HI": round(HI, 3), "Result": status
        }
        st.session_state.history.insert(0, new_data)
        st.rerun()

if st.session_state.history:
    st.table(pd.DataFrame(st.session_state.history))

st.markdown("</div>", unsafe_allow_html=True)