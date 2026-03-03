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

def draw_input_row(label, value, key, step=0.1, fmt="%.1f"):
    r_cols = st.columns([1.5, 1])
    with r_cols[0]:
        st.markdown(f"**{label}**")
    with r_cols[1]:
        return st.number_input(label, value=value, step=step, format=fmt, key=key, label_visibility="collapsed")

# ======================================================
# Header
# ======================================================
st.markdown(
    f'<div class="header">'
    f'<img src="https://raw.githubusercontent.com/jubailsanghoon/HeatInput2/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg">'
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
# 2. Main Layout (Inputs & Results)
# ======================================================
col_params, col_spacer, col_result = st.columns([1.2, 0.1, 1])

with col_params:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    voltage = draw_input_row("Voltage (V)", 30.0, "v")
    current = draw_input_row("Current (A)", 300.0, "c")
    length  = draw_input_row("Length (mm)", 5.0, "l")
    time_s  = draw_input_row("Time (sec)", 1.0, "t")

with col_result:
    st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
    w_min = draw_input_row("Min", 0.96, "min_val", step=0.01, fmt="%.2f")
    w_max = draw_input_row("Max", 2.50, "max_val", step=0.01, fmt="%.2f")
    
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    
    # 계산 로직
    HI = (k * voltage * current * time_s) / (length * 1000) if length > 0 else 0.0
    status = "PASS" if w_min <= HI <= w_max else "FAIL"
    
    # 결과 박스 가로 배치 (50% : 45% 및 5% 여백)
    # Streamlit 컬럼 비율로 구현하여 반응형 대응
    res_box_cols = st.columns([50, 5, 45])
    with res_box_cols[0]:
        st.markdown(f'<div class="result-box-value">{HI:.3f} kJ/mm</div>', unsafe_allow_html=True)
    with res_box_cols[2]:
        st.markdown(f'<div class="status-box {status.lower()}">{status}</div>', unsafe_allow_html=True)

# ======================================================
# 3. Save Data & Export CSV (같은 줄, 여백 5%)
# ======================================================
st.write("")
btn_row1 = st.columns([47.5, 5, 47.5])

with btn_row1[0]:
    if st.button("💾 Save Data"):
        new_entry = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Std": standard, "Prc": process, "HI": round(HI, 3), "Result": status,
            "V": voltage, "A": current, "L": length, "T": time_s
        }
        st.session_state.history.insert(0, new_entry)
        if len(st.session_state.history) > 50: st.session_state.history.pop()
        st.rerun()

with btn_row1[2]:
    if st.session_state.history:
        csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode("utf-8-sig")
        st.download_button(label="📤 Export CSV", data=csv, file_name=f"HI_{datetime.now().strftime('%m%d_%H%M')}.csv", mime="text/csv")
    else:
        st.button("📤 Export CSV", disabled=True)

# ======================================================
# 4. History & Clear (데이터 있을 때만 표시, 여백 5%)
# ======================================================
if st.session_state.history:
    st.write("")
    btn_row2 = st.columns([47.5, 5, 47.5])
    with btn_row2[0]:
        st.button("📋 Recent History", disabled=True)
    with btn_row2[2]:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

    # 히스토리 테이블
    st.markdown('<div class="section-title">History Table (Max 50)</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(st.session_state.history))

# ======================================================
# 5. Footer - 로고 및 연락처
# ======================================================
st.markdown(
    f'<div class="footer">'
    f'<img class="footer-logo-img" src="https://raw.githubusercontent.com/jubailsanghoon/HeatInput2/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg" />'
    f'<div class="footer-text"><b>Jubail.sanghoon@gmail.com</b></div>'
    f'</div>',
    unsafe_allow_html=True,
)