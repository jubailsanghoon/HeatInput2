import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 모바일 최적화 및 간격 극최소화 제어
# ======================================================
st.markdown("""
<style>
    /* 전체 여백 조정 */
    .block-container {
        padding-top: 1.5rem !important; 
        padding-bottom: 1rem !important;
        max-width: 800px !important;
    }
    
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 헤더 간격 최소화 */
    .header {
        display: flex;
        align-items: center;
        border-bottom: 3px solid black;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }
    .header img { height: 35px; margin-right: 10px; }
    .title { 
        font-size: clamp(18px, 5vw, 22px); 
        font-weight: 900; 
        color: black;
    }

    /* 섹션 제목 및 간격 최소화 */
    .section-title { 
        font-size: 14px; 
        font-weight: 900; 
        margin-top: 8px; 
        margin-bottom: 4px;
        color: black;
    }

    /* 결과 박스 스타일 */
    .result-box-value {
        width: 100%;
        font-size: clamp(14px, 4.2vw, 24px);
        font-weight: 900;
        padding: 10px 2px;
        background: #ffe5cc;
        border: 2px solid black;
        border-radius: 6px;
        text-align: center;
        color: black !important;
    }

    .status-box {
        width: 100%;
        font-size: clamp(14px, 4.2vw, 24px);
        font-weight: 900;
        padding: 10px 2px;
        border: 2px solid black;
        border-radius: 6px;
        text-align: center;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }

    /* 버튼 스타일 - 텍스트 최소화 및 크기 최적화 */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        background-color: #f0f0f0 !important;
        color: black !important;
        border: 2px solid black !important;
        border-radius: 6px !important;
        padding: 0px !important;
    }

    /* ★★★ 모바일 수평 배치 강제 및 간격 극최소화 ★★★ */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 4px !important; /* 요소 간 간격 4px로 제한 */
    }
    
    div[data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }

    /* 라디오 버튼 간격 조절 */
    div[data-testid="stWidgetLabel"] { display: none; }
    div[data-testid="stRadio"] > div { gap: 10px !important; }

    /* 푸터 스타일 */
    .footer {
        display: flex;
        justify-content: flex-start;
        margin-top: 30px;
        border-top: 1px solid #ddd;
        padding-top: 10px;
    }
    .footer-text {
        font-size: 12px;
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
    cols = st.columns([1, 1]) # 1:1 비율로 간격 최소화
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
# 1. Standard / Process (간격 최소화)
# ======================================================
c_std, c_prc = st.columns([1, 1.3])
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
col_input, col_result = st.columns([1, 1]) # 모바일에서 반반 배치

with col_input:
    st.markdown('<div class="section-title">Parameters</div>', unsafe_allow_html=True)
    volt = draw_input_row("Volt(V)", 30.0, "v_val")
    amp  = draw_input_row("Amp(A)", 300.0, "a_val")
    len_mm = draw_input_row("Len(mm)", 5.0, "l_val")
    time_s = draw_input_row("Time(s)", 1.0, "t_val")

with col_result:
    st.markdown('<div class="section-title">WPS Range</div>', unsafe_allow_html=True)
    wps_mode = st.radio("WPS Mode", ["Input", "No input"], horizontal=True, label_visibility="collapsed")
    
    if wps_mode == "Input":
        w_cols = st.columns([1, 1]) # Min/Max 간격 최소화
        with w_cols[0]:
            w_min = st.number_input("Min", value=0.96, step=0.01, format="%.2f", key="min_input", label_visibility="collapsed")
        with w_cols[1]:
            w_max = st.number_input("Max", value=2.50, step=0.01, format="%.2f", key="max_input", label_visibility="collapsed")
    else:
        w_min, w_max = 0.0, 0.0
        st.write("Range Off")

    st.markdown('<div class="section-title">Result</div>', unsafe_allow_html=True)
    hi_res = (k_val * volt * amp * time_s) / (len_mm * 1000) if len_mm > 0 else 0.0
    
    if wps_mode == "Input":
        res_status = "PASS" if w_min <= hi_res <= w_max else "FAIL"
        res_cols = st.columns([1, 1])
        with res_cols[0]:
            st.markdown(f'<div class="result-box-value">{hi_res:.3f}</div>', unsafe_allow_html=True)
        with res_cols[1]:
            st.markdown(f'<div class="status-box {res_status.lower()}">{res_status}</div>', unsafe_allow_html=True)
    else:
        res_status = "N/A"
        st.markdown(f'<div class="result-box-value">{hi_res:.3f} kJ/mm</div>', unsafe_allow_html=True)

# ======================================================
# 3. 버튼 레이아웃 - Save / Export (나란히 배치)
# ======================================================
st.write("")
btn_row1 = st.columns([1, 1])

with btn_row1[0]:
    if st.button("💾 Save"):
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
        st.download_button(label="📤 Export", data=csv_out, file_name=f"HI_{datetime.now().strftime('%m%d_%H%M')}.csv", mime="text/csv")
    else:
        st.button("📤 Export", disabled=True)

# ======================================================
# 4. 히스토리 관리 (나란히 배치)
# ======================================================
if st.session_state.history:
    btn_row2 = st.columns([1.5, 1])
    with btn_row2[0]:
        st.markdown('<div class="section-title">Recent History</div>', unsafe_allow_html=True)
    with btn_row2[1]:
        if st.button("🗑️ Clear"):
            st.session_state.history = []
            st.rerun()
    st.table(pd.DataFrame(st.session_state.history).head(10))

# ======================================================
# 5. Footer (이메일 소문자 및 왼쪽 정렬)
# ======================================================
st.markdown(
    f'<div class="footer">'
    f'<div class="footer-text"><b>jubail.sanghoon@gmail.com</b></div>'
    f'</div>',
    unsafe_allow_html=True
)