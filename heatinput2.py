import streamlit as st
import pandas as pd
from datetime import datetime

# ======================================================
# 1. 페이지 기본 설정
# ======================================================
st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# 2. CSS - 화이트 테마 및 주황색 포인트 디자인
# ======================================================
st.markdown("""
<style>
    /* 전체 배경 및 텍스트 블랙 고정 */
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
    
    /* [수정] 헤더 영역: 주황색 수평선(5px) 및 타이틀 크기(32px) */
    .header {
        display: flex;
        align-items: center;
        border-bottom: 5px solid #ff7f00; 
        padding-bottom: 12px;
        margin-bottom: 15px;
    }
    .header img { 
        height: 50px; 
        margin-right: 15px; 
    }
    .title { 
        font-size: 32px; 
        font-weight: 900; 
        letter-spacing: -1px;
    }

    .section-title { font-size: 16px; font-weight: 900; margin-top: 12px; margin-bottom: 8px; }
    
    /* 결과창 디자인 */
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
    }
    .pass, .fail {
        font-size: 24px;
        font-weight: 900;
        padding: 12px;
        border: 1px solid #cccccc;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 12px;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }
    
    /* 버튼 스타일 */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 60px !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        background-color: #f0f0f0 !important;
        color: black !important;
        border: 2px solid black !important;
        border-radius: 4px !important;
    }
    
    /* 입력창 스타일 */
    input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    .k-info { font-size: 13px; color: #555 !important; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 3. 데이터 및 로직 설정
# ======================================================
EFFICIENCY = {
    "SAW":  {"AWS": 1.0, "ISO": 1.0},
    "GMAW": {"AWS": 1.0, "ISO": 0.8},
    "FCAW": {"AWS": 1.0, "ISO": 0.8},
    "SMAW": {"AWS": 1.0, "ISO": 0.8},
}

def validate_inputs(v, a, l, t):
    errs = []
    if v <= 0: errs.append("Volt > 0")
    if a <= 0: errs.append("Amp > 0")
    if l <= 0: errs.append("Len > 0")
    if t <= 0: errs.append("Time > 0")
    return errs

# 세션 상태 초기화
if "history" not in st.session_state:
    st.session_state.history = []

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ======================================================
# 4. Header (SyntaxError 수정 포인트)
# ======================================================
st.markdown(f"""
    <div class="header">
        <img src="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg">
        <div class="title">Heat Input Master</div>
    </div>
""", unsafe_allow_html=True)

# ======================================================
# 5. 메인 레이아웃 시공
# ======================================================

# 5.1 Standard & Process
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS", "ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True, label_visibility="collapsed")

k = EFFICIENCY[process][standard]
st.markdown(f'<div class="k-info">Thermal Efficiency (k) = <b>{k}</b> | {standard} / {process}</div>', unsafe_allow_html=True)

# 5.2 WPS Range
st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
w_cols = st.columns([1, 4, 1, 4])
with w_cols[0]: st.markdown("**Min**")
with w_cols[1]: min_range = st.number_input("min", value=0.96, step=0.01, format="%.2f", label_visibility="collapsed")
with w_cols[2]: st.markdown("**Max**")
with w_cols[3]: max_range = st.number_input("max", value=2.50, step=0.01, format="%.2f", label_visibility="collapsed")

# 5.3 파라미터 입력 및 실시간 결과
st.write("")
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    # 가독성을 위한 수동 행 구성
    def draw_row(lab, val, k):
        c1, c2 = st.columns([1.5, 2])
        c1.markdown(f"**{lab}**")
        return c2.number_input(lab, value=val, step=0.1, format="%.1f", key=k, label_visibility="collapsed")
    
    voltage = draw_row("Volt (V)", 30.0, "v")
    current = draw_row("Amp (A)", 300.0, "c")
    length  = draw_row("Len (mm)", 5.0, "l")
    time_s  = draw_row("Time (s)", 1.0, "t")

errors = validate_inputs(voltage, current, length, time_s)
HI = (k * voltage * current * time_s) / (length * 1000) if not errors else 0.0
status = "PASS" if min_range <= HI <= max_range else "FAIL"

with col_right:
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{round(HI, 3)} kJ/mm</div>', unsafe_allow_html=True)
    if errors:
        st.markdown('<div class="fail">INPUT ERR</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="{status.lower()}">{status}</div>', unsafe_allow_html=True)

# 5.4 추가 정보 입력
st.markdown('<div class="section-title">Additional Info</div>', unsafe_allow_html=True)
opt1, opt2 = st.columns(2)
wps_no = opt1.text_input("WPS No.", placeholder="WPS-001")
welder_no = opt2.text_input("Welder No.", placeholder="W-123")

# 5.5 버튼 구역
st.write("")
b_left, b_right = st.columns(2)
if b_left.button("Save Data", disabled=bool(errors)):
    new_entry = {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "WPS": wps_no if wps_no else "-",
        "Welder": welder_no if welder_no else "-",
        "Std": standard, "Prc": process, "HI": round(HI, 3), "Result": status,
        "V": voltage, "A": current, "L": length, "T": time_s
    }
    st.session_state.history.insert(0, new_entry)
    st.toast("Saved!")
    st.rerun()

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    csv = df.to_csv(index=False).encode("utf-8-sig")
    b_right.download_button("Export CSV", data=csv, file_name="HI_Data.csv", mime="text/csv")

# 5.6 히스토리 표시
if st.session_state.history:
    st.markdown('<div class="section-title">History</div>', unsafe_allow_html=True)
    if st.button("Clear All"):
        st.session_state.history = []
        st.rerun()
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)