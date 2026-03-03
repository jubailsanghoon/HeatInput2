import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 레이아웃 안정화 및 가독성 중심 디자인 (모바일 대응 포함)
# ======================================================
st.markdown("""
<style>
    /* 전체 여백 조정 */
    .block-container {
        padding-top: 2.5rem !important; 
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }
    
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 헤더 디자인 */
    .header {
        display: flex;
        align-items: center;
        border-bottom: 4px solid black;
        padding-bottom: 8px;
        margin-top: 0px; 
        margin-bottom: 25px;
    }
    .header img { height: 45px; margin-right: 15px; }
    .title { 
        font-size: 24px; 
        font-weight: 900; 
        color: black;
    }

    /* 섹션 제목 */
    .section-title { 
        font-size: 18px; 
        font-weight: 900; 
        margin-top: 20px; 
        margin-bottom: 10px;
        color: black;
    }

    /* 결과 박스 스타일 */
    .result-box-value {
        width: 100%;
        font-size: 26px;
        font-weight: 900;
        padding: 15px 5px;
        background: #ffe5cc;
        border: 2px solid black;
        border-radius: 8px;
        text-align: center;
        color: black !important;
        margin-bottom: 10px;
    }

    .status-box {
        width: 100%;
        font-size: 26px;
        font-weight: 900;
        padding: 15px 5px;
        border: 2px solid black;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }

    /* 버튼 스타일 */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 60px !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        background-color: #f0f0f0 !important;
        color: black !important;
        border: 2px solid black !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #e0e0e0 !important;
    }

    /* 수평 배치 유지 (모바일 환경 고려) */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    /* 푸터 스타일 */
    .footer {
        display: flex;
        justify-content: flex-start;
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
# 1. Standard / Process
# ======================================================
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS", "ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True, label_visibility="collapsed")

k_val = EFFICIENCY[process][standard]

# ======================================================
# 2. 메인 레이아웃 (Input Parameters & WPS/Result)
# ======================================================
st.write("---")
col_input, col_gap, col_result = st.columns([1.2, 0.1, 1.1])

with col_input:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    volt = draw_input_row("Voltage (V)", 30.0, "v_val")
    amp  = draw_input_row("Current (A)", 300.0, "c_val")
    len_mm = draw_input_row("Length (mm)", 5.0, "l_val")
    time_s = draw_input_row("Time (sec)", 1.0, "t_val")

with col_result:
    st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
    # WPS Range 모드 선택 (Input / No input)
    wps_mode = st.radio("WPS Mode", ["Input", "No input"], horizontal=True, label_visibility="collapsed")
    
    # [Min/Max 나란히 배치 유지] - WPS Mode와 상관없이 레이아웃 고정
    w_cols = st.columns([1, 1])
    with w_cols[0]:
        m_row = st.columns([0.8, 1.2])
        with m_row[0]: st.markdown("**Min.**")
        with m_row[1]: 
            w_min = st.number_input("Min", value=0.96, step=0.01, format="%.2f", key="min_input", label_visibility="collapsed", disabled=(wps_mode == "No input"))
    with w_cols[1]:
        x_row = st.columns([0.8, 1.2])
        with x_row[0]: st.markdown("**Max.**")
        with x_row[1]: 
            w_max = st.number_input("Max", value=2.50, step=0.01, format="%.2f", key="max_input", label_visibility="collapsed", disabled=(wps_mode == "No input"))

    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    hi_res = (k_val * volt * amp * time_s) / (len_mm * 1000) if len_mm > 0 else 0.0
    
    if wps_mode == "Input":
        # 판정 결과 포함 (PASS/FAIL)
        res_status = "PASS" if w_min <= hi_res <= w_max else "FAIL"
        res_cols = st.columns([0.55, 0.45])
        with res_cols[0]:
            st.markdown(f'<div class="result-box-value">{hi_res:.3f}</div>', unsafe_allow_html=True)
        with res_cols[1]:
            st.markdown(f'<div class="status-box {res_status.lower()}">{res_status}</div>', unsafe_allow_html=True)
    else:
        # No input인 경우 판정 안함 (수치만 표시)
        res_status = "N/A"
        st.markdown(f'<div class="result-box-value">{hi_res:.3f} kJ/mm</div>', unsafe_allow_html=True)

# ======================================================
# 3. 버튼 레이아웃 - Save / Export (나란히 배치)
# ======================================================
st.write("")
btn_row1 = st.columns([1, 1])

with btn_row1[0]:
    if st.button("💾 Save"):
        # 로컬 시스템 시간을 사용하여 데이터 저장
        entry = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Std": standard, "Prc": process, "HI": round(hi_res, 3), "Res": res_status,
            "V": volt, "A": amp, "L": len_mm, "T": time_s
        }
        st.session_state.history.insert(0, entry)
        if len(st.session_state.history) > 50: st.session_state.history.pop()
        st.rerun()

with btn_row1[1]:
    if st.session_state.history:
        csv_out = pd.DataFrame(st.session_state.history).to_csv(index=False).encode("utf-8-sig")
        st.download_button(label="📤 Export", data=csv_out, file_name=f"HeatInput_{datetime.now().strftime('%m%d_%H%M')}.csv", mime="text/csv")
    else:
        st.button("📤 Export", disabled=True)

# ======================================================
# 4. 히스토리 관리 (Clear History 버튼만 유지)
# ======================================================
if st.session_state.history:
    st.write("---")
    btn_row2 = st.columns([1, 1])
    # Recent History 버튼 박스 삭제 후 Clear History 버튼만 우측 배치 유지
    with btn_row2[1]:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

    st.markdown('<div class="section-title">History Records (Max 50)</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(st.session_state.history))

# ======================================================
# 5. Footer (이메일 및 왼쪽 정렬)
# ======================================================
st.markdown(
    f'<div class="footer">'
    f'<div class="footer-text"><b>jubail.sanghoon@gmail.com</b></div>'
    f'</div>',
    unsafe_allow_html=True
)