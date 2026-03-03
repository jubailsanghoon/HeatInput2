import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(layout="centered", page_title="Heat Input Master")

# ======================================================
# CSS - 화이트 테마 고정 및 모바일 최적화
# ======================================================
st.markdown("""
<style>
    /* 1. 화이트 테마 강제 고정 */
    [data-testid="stAppViewContainer"], .main-container, .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* 텍스트 색상 및 입력창 테두리 고정 */
    h1, h2, h3, p, span, div, label, .stMarkdown {
        color: #000000 !important;
    }

    /* 2. 모바일 컨테이너 최적화 */
    .main-container { 
        max-width: 100% !important; 
        margin: auto; 
        font-family: 'Segoe UI', sans-serif; 
        padding: 10px;
    }

    /* Header */
    .header { display:flex; align-items:center; border-bottom:4px solid black; padding-bottom:10px; margin-bottom:15px; }
    .header img { height:40px; margin-right:10px; }
    .title { font-size:22px; font-weight:900; }

    /* Section Title */
    .section-title { font-size:16px; font-weight:900; margin-top:12px; margin-bottom:8px; }

    /* Result Boxes */
    .result-box { font-size:24px; font-weight:900; padding:12px; background:#ffe5cc; border:2px solid black; text-align: center; margin-bottom: 8px; color: black !important; }
    .pass, .fail { font-size:24px; font-weight:900; padding:12px; border:2px solid black; text-align: center; margin-bottom: 12px; }
    .pass { background:#00cc44; color:white !important; }
    .fail { background:#ff7f00; color:white !important; }

    /* 버튼 스타일 (화이트 테마에 어울리는 회색조) */
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

    /* 입력창 배경 화이트 고정 */
    input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }

    /* 모바일에서 수평 정렬 유지 */
    div[data-testid="stHorizontalBlock"] { 
        align-items: center; 
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'history' not in st.session_state:
    st.session_state.history = []

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ======================================================
# Header
# ======================================================
st.markdown(f"""
<div class="header">
<img src="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg">
<div class="title">Heat Input Master</div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# 1️⃣ Standard & Process Selection
# ======================================================
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS", "ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True, label_visibility="collapsed")

# ======================================================
# 2️⃣ WPS Range
# ======================================================
st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
w_cols = st.columns([0.5, 1.5, 0.5, 1.5])

with w_cols[0]: st.markdown("**Min**")
with w_cols[1]: min_range = st.number_input("min", value=0.96, step=0.01, format="%.2f", label_visibility="collapsed")
with w_cols[2]: st.markdown("**Max**")
with w_cols[3]: max_range = st.number_input("max", value=2.50, step=0.01, format="%.2f", label_visibility="collapsed")

# ======================================================
# 3️⃣ Input Parameters & Live Result
# ======================================================
st.write("")
# 모바일 대응을 위해 컬럼 비율 조정
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    
    def draw_input_row(label, value, key):
        r_cols = st.columns([1.5, 2])
        with r_cols[0]: st.markdown(f"**{label}**")
        with r_cols[1]: return st.number_input(label, value=value, step=0.1, format="%.1f", key=key, label_visibility="collapsed")

    voltage = draw_input_row("Volt (V)", 30.0, "v")
    current = draw_input_row("Amp (A)", 300.0, "c")
    length = draw_input_row("Len (mm)", 5.0, "l")
    time = draw_input_row("Time (s)", 1.0, "t")

# 계산 로직
k = 1.0 if standard == "AWS" else {"SAW": 1.0, "GMAW": 0.8, "FCAW": 0.8, "SMAW": 0.8}.get(process, 0.8)
HI = (k * voltage * current * time) / (length * 1000) if length > 0 else 0
status = "PASS" if min_range <= HI <= max_range else "FAIL"

with col_right:
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{HI:.3f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="{status.lower()}">{status}</div>', unsafe_allow_html=True)

# ======================================================
# 4️⃣ 버튼 구역
# ======================================================
b_cols = st.columns(2)

with b_cols[0]:
    if st.button("Save Data"):
        new_entry = {"Time": datetime.now().strftime("%H:%M:%S"), "Std": standard, "Prc": process,
                     "HI": round(HI, 3), "Res": status, "V": voltage, "A": current, "L": length, "T": time}
        st.session_state.history.insert(0, new_entry)
        if len(st.session_state.history) > 50: st.session_state.history.pop()
        st.rerun()

with b_cols[1]:
    if st.session_state.history:
        csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="Export", data=csv,
                           file_name=f"HI_{datetime.now().strftime('%m%d_%H%M')}.csv", mime="text/csv")
    else:
        st.button("Export", disabled=True)

# ======================================================
# 5️⃣ 히스토리 테이블 (모바일에서 보기 편하게 폰트 조절)
# ======================================================
if st.session_state.history:
    st.markdown('<div class="section-title">Recent History</div>', unsafe_allow_html=True)
    # 모바일에서 테이블이 너무 크면 스크롤이 생깁니다.
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)