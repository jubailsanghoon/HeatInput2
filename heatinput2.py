import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 레이아웃 및 디자인 최적화
# ======================================================
st.markdown("""
<style>
    /* 전체 배경 및 기본 폰트 설정 */
    [data-testid="stAppViewContainer"], .main-container, .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* 상단 여백 최소화 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    .main-container {
        max-width: 100% !important;
        margin: auto;
        font-family: 'Segoe UI', sans-serif;
    }

    /* 헤더 디자인 - 폰트 사이즈 확대 및 여백 최소화 */
    .header {
        display: flex;
        align-items: center;
        border-bottom: 5px solid black;
        padding-bottom: 5px;
        margin-top: -20px; /* 위쪽 여백 최소화 */
        margin-bottom: 15px;
    }
    .header img { height: 50px; margin-right: 15px; }
    .title { 
        font-size: 54px; /* 폰트 사이즈 더 키우기 */
        font-weight: 900; 
        line-height: 1.1;
    }

    .section-title { font-size: 18px; font-weight: 900; margin-top: 15px; margin-bottom: 10px; }

    /* 결과 박스 공통 스타일 */
    .result-container {
        display: flex;
        align-items: center;
        gap: 0px; /* 간격은 st.columns에서 제어 */
        margin-bottom: 10px;
    }

    .result-box-value {
        font-size: 26px;
        font-weight: 900;
        padding: 15px;
        background: #ffe5cc;
        border: 2px solid black;
        text-align: center;
        color: black !important;
        width: 100%;
    }

    .status-box {
        font-size: 26px;
        font-weight: 900;
        padding: 15px;
        border: 2px solid black;
        text-align: center;
        width: 100%;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }
    .no-wps { background: #f0f0f0; color: black !important; }

    /* 버튼 디자인 - 검정 테두리 강조 */
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
    
    /* 입력창 디자인 */
    input {
        border: 2px solid #000000 !important;
    }

    /* 푸터 디자인 */
    .footer {
        display: flex;
        align-items: center;
        margin-top: 30px;
        border-top: 1px solid #eeeeee;
        padding-top: 10px;
    }
    .footer-logo-img {
        height: 30px;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 로직용 데이터 및 함수
# ======================================================
EFFICIENCY = {
    "SAW":  {"AWS": 1.0, "ISO": 1.0},
    "GMAW": {"AWS": 1.0, "ISO": 0.8},
    "FCAW": {"AWS": 1.0, "ISO": 0.8},
    "SMAW": {"AWS": 1.0, "ISO": 0.8},
}

def draw_input_row(label, value, key, step=0.1, fmt="%.1f"):
    r_cols = st.columns([1.5, 1])
    with r_cols[0]:
        st.markdown(f"**{label}**")
    with r_cols[1]:
        return st.number_input(label, value=value, step=step, format=fmt, key=key, label_visibility="collapsed")

if "history" not in st.session_state:
    st.session_state.history = []

# ======================================================
# Header
# ======================================================
st.markdown(
    f'<div class="header">'
    f'<img src="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg">'
    f'<div class="title">Heat Input Master</div>'
    f'</div>',
    unsafe_allow_html=True
)

# ======================================================
# 1. Standard / Process
# ======================================================
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard Selection</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS", "ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Select Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True, label_visibility="collapsed")

k = EFFICIENCY[process][standard]

# ======================================================
# 2. Input Parameters & Live Result (레이아웃 통합)
# ======================================================
col_params, col_spacer, col_result = st.columns([1.2, 0.1, 1])

with col_params:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    voltage = draw_input_row("Volt (V)", 30.0, "v")
    current = draw_input_row("Amp (A)", 300.0, "c")
    length  = draw_input_row("Len (mm)", 5.0, "l")
    time_s  = draw_input_row("Time (s)", 1.0, "t")

with col_result:
    st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
    w_min = draw_input_row("Min", 0.96, "min_val", step=0.01, fmt="%.2f")
    w_max = draw_input_row("Max", 2.50, "max_val", step=0.01, fmt="%.2f")
    
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    
    # 계산
    HI = (k * voltage * current * time_s) / (length * 1000) if length > 0 else 0.0
    status = "PASS" if w_min <= HI <= w_max else "FAIL"
    
    # [Live Result] 결과값과 PASS 박스를 같은 라인에 배치 (PASS 45% 폭)
    # 컬럼 비중: 55% (결과값) : 45% (상태)
    res_col1, res_col2 = st.columns([0.55, 0.45])
    with res_col1:
        st.markdown(f'<div class="result-box-value">{HI:.3f} kJ/mm</div>', unsafe_allow_html=True)
    with res_col2:
        st.markdown(f'<div class="status-box {status.lower()}">{status}</div>', unsafe_allow_html=True)

# ======================================================
# 3. 버튼 구역 - Save Data / Export CSV (5% 여백)
# ======================================================
st.write("")
# 버튼 비율: 47.5% : 5% (여백) : 47.5%
btn_cols1 = st.columns([0.475, 0.05, 0.475])

with btn_cols1[0]:
    if st.button("💾 Save Data"):
        new_entry = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Std": standard, "Prc": process, "HI": round(HI, 3), "Result": status,
            "V": voltage, "A": current, "L": length, "T": time_s, "Min": w_min, "Max": w_max
        }
        st.session_state.history.insert(0, new_entry)
        if len(st.session_state.history) > 50: st.session_state.history.pop()
        st.rerun()

with btn_cols1[2]:
    if st.session_state.history:
        csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode("utf-8-sig")
        st.download_button(label="📤 Export CSV", data=csv, file_name=f"HI_{datetime.now().strftime('%m%d_%H%M')}.csv", mime="text/csv")
    else:
        st.button("📤 Export CSV", disabled=True)

# ======================================================
# 4. 버튼 구역 - History / Clear (데이터 있을 때만 표시, 5% 여백)
# ======================================================
if st.session_state.history:
    btn_cols2 = st.columns([0.475, 0.05, 0.475])
    with btn_cols2[0]:
        st.button("📋 Recent History", disabled=True) # 현재는 리스트 표시용으로만 사용
    with btn_cols2[2]:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

    # 히스토리 테이블 표시
    st.markdown('<div class="section-title">Recent History (최근 50건)</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(st.session_state.history))

# ======================================================
# 5. Footer - 로고 교체
# ======================================================
st.markdown(
    f'<div class="footer">'
    f'<img class="footer-logo-img" src="https://raw.githubusercontent.com/jubailsanghoon/HeatInput2/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg" />'
    f'<div class="footer-text"><b>Jubail.sanghoon@gmail.com</b></div>'
    f'</div>',
    unsafe_allow_html=True,
)