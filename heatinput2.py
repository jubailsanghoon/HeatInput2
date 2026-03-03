import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 레이아웃 및 디자인 정밀 조정
# ======================================================
st.markdown("""
<style>
    /* 상단 여백 및 앱 전체 배경 설정 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }
    
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 헤더 - 여백 최소화 및 폰트 크기 확대 */
    .header {
        display: flex;
        align-items: center;
        border-bottom: 5px solid black;
        padding-bottom: 10px;
        margin-bottom: 25px;
    }
    .header img { height: 60px; margin-right: 20px; }
    .title { 
        font-size: 48px; 
        font-weight: 900; 
        line-height: 1.1;
        color: black;
    }

    .section-title { 
        font-size: 20px; 
        font-weight: 900; 
        margin-top: 20px; 
        margin-bottom: 12px;
        color: black;
    }

    /* 결과 박스 스타일 */
    .result-box-value {
        font-size: 28px;
        font-weight: 900;
        padding: 15px;
        background: #ffe5cc;
        border: 2px solid black;
        text-align: center;
        color: black !important;
        margin-bottom: 10px;
    }

    .status-box {
        font-size: 28px;
        font-weight: 900;
        padding: 15px;
        border: 2px solid black;
        text-align: center;
        margin-bottom: 10px;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }

    /* 버튼 스타일 */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 65px !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        background-color: #f0f0f0 !important;
        color: black !important;
        border: 3px solid black !important;
        border-radius: 4px !important;
    }

    /* 푸터 디자인 */
    .footer {
        display: flex;
        align-items: center;
        margin-top: 40px;
        border-top: 1px solid #eeeeee;
        padding-top: 20px;
    }
    .footer-logo-img {
        height: 40px;
        margin-right: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 로직 및 세션 상태 초기화
# ======================================================
EFFICIENCY = {
    "SAW":  {"AWS": 1.0, "ISO": 1.0},
    "GMAW": {"AWS": 1.0, "ISO": 0.8},
    "FCAW": {"AWS": 1.0, "ISO": 0.8},
    "SMAW": {"AWS": 1.0, "ISO": 0.8},
}

if "history" not in st.session_state:
    st.session_state.history = []

# 입력창을 한 줄에 배치하기 위한 헬퍼 함수
def draw_input_row(label, value, key, step=0.1, fmt="%.1f"):
    cols = st.columns([1, 1])
    with cols[0]:
        st.write(f"**{label}**")
    with cols[1]:
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
# 1. Standard / Process 선택
# ======================================================
st.markdown('<div class="section-title">Standard & Process</div>', unsafe_allow_html=True)
c_std, c_prc = st.columns([1, 1])
with c_std:
    standard = st.radio("Standard", ["AWS", "ISO"], horizontal=True)
with c_prc:
    process = st.radio("Process", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True)

k = EFFICIENCY[process][standard]

# ======================================================
# 2. 메인 레이아웃 (입력창 및 결과창)
# ======================================================
st.write("---")
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
    
    # 결과 표시
    st.markdown(f'<div class="result-box-value">{HI:.3f} kJ/mm</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-box {status.lower()}">{status}</div>', unsafe_allow_html=True)

# ======================================================
# 3. 버튼 구역 (저장 및 내보내기)
# ======================================================
st.write("")
btn_row1 = st.columns([1, 0.1, 1])

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
# 4. 히스토리 관리 (데이터 있을 때만 표시)
# ======================================================
if st.session_state.history:
    st.write("---")
    btn_row2 = st.columns([1, 0.1, 1])
    with btn_row2[0]:
        st.button("📋 History Loaded", disabled=True)
    with btn_row2[2]:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

    st.markdown('<div class="section-title">History Table (Max 50)</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(st.session_state.history))

# ======================================================
# 5. Footer
# ======================================================
st.markdown(
    f'<div class="footer">'
    f'<img class="footer-logo-img" src="https://raw.githubusercontent.com/jubailsanghoon/HeatInput2/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg" />'
    f'<div class="footer-text"><b>Jubail.sanghoon@gmail.com</b></div>'
    f'</div>',
    unsafe_allow_html=True,