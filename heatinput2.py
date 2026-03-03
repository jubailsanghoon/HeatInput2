import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 레이아웃 및 디자인 정밀 제어
# ======================================================
st.markdown("""
<style>
    /* 상단 여백 최소화 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }
    
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 헤더 - 폰트 사이즈 조정 및 여백 최적화 */
    .header {
        display: flex;
        align-items: center;
        border-bottom: 4px solid black;
        padding-bottom: 8px;
        margin-top: -20px; 
        margin-bottom: 25px;
    }
    .header img { height: 50px; margin-right: 20px; }
    .title { 
        font-size: 40px; /* 기존 64px에서 3단계 축소 */
        font-weight: 900; 
        line-height: 1;
        color: black;
    }

    .section-title { 
        font-size: 18px; 
        font-weight: 900; 
        margin-top: 15px; 
        margin-bottom: 10px;
        color: black;
    }

    /* 결과 박스 스타일 - 라운드 형태로 복구 */
    .result-box-value {
        width: 100%;
        font-size: 28px;
        font-weight: 900;
        padding: 15px 5px;
        background: #ffe5cc;
        border: 2px solid black;
        border-radius: 8px;
        text-align: center;
        color: black !important;
    }

    .status-box {
        width: 100%;
        font-size: 28px;
        font-weight: 900;
        padding: 15px 5px;
        border: 2px solid black;
        border-radius: 8px;
        text-align: center;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }

    /* 버튼 스타일 - 라운드 형태로 복구 */
    .stButton, .stDownloadButton {
        width: 100% !important;
    }
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 65px !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        background-color: #f0f0f0 !important;
        color: black !important;
        border: 2px solid black !important;
        border-radius: 8px !important;
        padding: 0px !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #e0e0e0 !important;
        border-color: #000000 !important;
    }

    /* 입력 필드 정렬 */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    
    /* 푸터 스타일 - 로고 삭제 대응 */
    .footer {
        display: flex;
        justify-content: center;
        margin-top: 50px;
        border-top: 1px solid #ddd;
        padding-top: 20px;
    }
    .footer-text {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 로직 및 세션 데이터 초기화
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
    cols = st.columns([1.5, 1])
    with cols[0]:
        st.markdown(f"**{label}**")
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
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard Selection</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS", "ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Select Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True, label_visibility="collapsed")

k_val = EFFICIENCY[process][standard]

# ======================================================
# 2. 메인 레이아웃 (Inputs & Result)
# ======================================================
st.write("---")
col_input, col_gap, col_result = st.columns([1.2, 0.1, 1.1])

with col_input:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    volt = draw_input_row("Voltage (V)", 30.0, "v_val")
    amp  = draw_input_row("Current (A)", 300.0, "a_val")
    len_mm = draw_input_row("Length (mm)", 5.0, "l_val")
    time_s = draw_input_row("Time (sec)", 1.0, "t_val")

with col_result:
    st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
    w_min = draw_input_row("Min", 0.96, "min_range", step=0.01, fmt="%.2f")
    w_max = draw_input_row("Max", 2.50, "max_range", step=0.01, fmt="%.2f")
    
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    
    # 입열량 계산: HI = (k * V * A * t) / (L * 1000)
    hi_res = (k_val * volt * amp * time_s) / (len_mm * 1000) if len_mm > 0 else 0.0
    res_status = "PASS" if w_min <= hi_res <= w_max else "FAIL"
    
    # [결과값 50% | 여백 5% | PASS-FAIL 45%] 한 줄 배치
    res_cols = st.columns([0.5, 0.05, 0.45])
    with res_cols[0]:
        st.markdown(f'<div class="result-box-value">{hi_res:.3f} kJ/mm</div>', unsafe_allow_html=True)
    with res_cols[2]:
        st.markdown(f'<div class="status-box {res_status.lower()}">{res_status}</div>', unsafe_allow_html=True)

# ======================================================
# 3. 버튼 레이아웃 - Save Data / Export CSV (5% 여백)
# ======================================================
st.write("")
btn_row1 = st.columns([0.475, 0.05, 0.475])

with btn_row1[0]:
    if st.button("💾 Save Data"):
        entry = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Std": standard, "Process": process, "HI": round(hi_res, 3), "Result": res_status,
            "V": volt, "A": amp, "L": len_mm, "T": time_s
        }
        st.session_state.history.insert(0, entry)
        if len(st.session_state.history) > 50: st.session_state.history.pop()
        st.rerun()

with btn_row1[2]:
    if st.session_state.history:
        csv_out = pd.DataFrame(st.session_state.history).to_csv(index=False).encode("utf-8-sig")
        st.download_button(label="📤 Export CSV", data=csv_out, file_name=f"HeatInput_{datetime.now().strftime('%m%d_%H%M')}.csv", mime="text/csv")
    else:
        st.button("📤 Export CSV", disabled=True)

# ======================================================
# 4. 히스토리 관리 (데이터 존재 시에만 표시)
# ======================================================
if st.session_state.history:
    st.write("")
    btn_row2 = st.columns([0.475, 0.05, 0.475])
    with btn_row2[0]:
        st.button("📋 Recent History", disabled=True)
    with btn_row2[2]:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

    st.markdown('<div class="section-title">History Records (Max 50)</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(st.session_state.history))

# ======================================================
# 5. Footer - 이메일만 표시 (로고 삭제)
# ======================================================
st.markdown(
    f'<div class="footer">'
    f'<div class="footer-text"><b>Jubail.sanghoon@gmail.com</b></div>'
    f'</div>',
    unsafe_allow_html=True
)