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
        border-bottom: 4px solid black;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .header img { height: 40px; margin-right: 10px; }
    .title { font-size: 22px; font-weight: 900; }
    .section-title { font-size: 16px; font-weight: 900; margin-top: 12px; margin-bottom: 8px; }
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
        box-shadow: none;
    }
    .pass, .fail {
        font-size: 24px;
        font-weight: 900;
        padding: 12px;
        border: 1px solid #cccccc;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: none;
    }
    .pass { background: #00cc44; color: white !important; }
    .fail { background: #ff7f00; color: white !important; }
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
    .k-info { font-size: 13px; color: #555 !important; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 열효율(k) 테이블 - AWS D1.1 / ISO 1011 기준
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
    if voltage <= 0:
        errors.append("전압(Volt)은 0보다 커야 합니다.")
    if current <= 0:
        errors.append("전류(Amp)는 0보다 커야 합니다.")
    if length <= 0:
        errors.append("비드 길이(Len)는 0보다 커야 합니다.")
    if time_s <= 0:
        errors.append("시간(Time)은 0보다 커야 합니다.")
    if voltage > 100:
        errors.append("전압(Volt)이 비현실적입니다 (최대 100V).")
    if current > 2000:
        errors.append("전류(Amp)가 비현실적입니다 (최대 2000A).")
    return errors

# ======================================================
# 입력 행 렌더링 헬퍼
# ======================================================
def draw_input_row(label, value, key, step=0.1, fmt="%.1f"):
    r_cols = st.columns([1.5, 2])
    with r_cols[0]:
        st.markdown("**" + label + "**")
    with r_cols[1]:
        return st.number_input(label, value=value, step=step, format=fmt, key=key, label_visibility="collapsed")

# ======================================================
# 세션 상태 초기화
# ======================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "wps_no" not in st.session_state:
    st.session_state.wps_no = ""
if "welder_no" not in st.session_state:
    st.session_state.welder_no = ""
if "joint_no" not in st.session_state:
    st.session_state.joint_no = ""
if "pass_type" not in st.session_state:
    st.session_state.pass_type = "Root"

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ======================================================
# Header
# ======================================================
st.markdown(
    '<div class="header">'
    '<img src="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg">'
    '<div class="title">Heat Input Master</div>'
    '</div>',
    unsafe_allow_html=True
)

# ======================================================
# 1. Standard & Process Selection
# ======================================================
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS", "ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True, label_visibility="collapsed")

# 열효율 k 결정
k = EFFICIENCY[process][standard]
st.markdown(
    '<div class="k-info">Thermal Efficiency (k) = <b>' + str(k) + '</b> &nbsp;|&nbsp; ' + standard + ' / ' + process + '</div>',
    unsafe_allow_html=True
)

# ======================================================
# 2. WPS Range
# ======================================================
st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
w_cols = st.columns([0.5, 1.5, 0.5, 1.5])
with w_cols[0]:
    st.markdown("**Min**")
with w_cols[1]:
    min_range = st.number_input("min", value=0.96, step=0.01, format="%.2f", label_visibility="collapsed")
with w_cols[2]:
    st.markdown("**Max**")
with w_cols[3]:
    max_range = st.number_input("max", value=2.50, step=0.01, format="%.2f", label_visibility="collapsed")

if min_range >= max_range:
    st.warning("WPS Min 값은 Max 값보다 작아야 합니다.")

# ======================================================
# 3. Input Parameters & Live Result
# ======================================================
st.write("")
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    voltage = draw_input_row("Volt (V)", 30.0, "v")
    current = draw_input_row("Amp (A)", 300.0, "c")
    length  = draw_input_row("Len (mm)", 5.0, "l")
    time_s  = draw_input_row("Time (s)", 1.0, "t")

# 유효성 검사
errors = validate_inputs(voltage, current, length, time_s)

# 계산 로직
# HI (kJ/mm) = k x V x A x t / (L x 1000)  [x1000: J -> kJ 변환]
if not errors:
    HI = (k * voltage * current * time_s) / (length * 1000)
    if min_range <= HI <= max_range:
        status = "PASS"
    else:
        status = "FAIL"
else:
    HI = 0.0
    status = "FAIL"

with col_right:
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    st.markdown('<div class="result-box">' + str(round(HI, 3)) + ' kJ/mm</div>', unsafe_allow_html=True)
    if errors:
        st.markdown('<div class="fail">INPUT ERR</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="' + status.lower() + '">' + status + '</div>', unsafe_allow_html=True)

# 유효성 오류 표시
for err in errors:
    st.error(err)

# ======================================================
# 4. 버튼 구역
# ======================================================
st.write("")
b_cols = st.columns([10, 1, 10])

with b_cols[0]:
    save_disabled = bool(errors) or (min_range >= max_range)
    if st.button("Save Data", disabled=save_disabled):
        new_entry = {
            "Time":      datetime.now().strftime("%H:%M:%S"),
            "WPS No.":   st.session_state.wps_no if st.session_state.wps_no else "-",
            "Pass":      st.session_state.pass_type,
            "Welder":    st.session_state.welder_no if st.session_state.welder_no else "-",
            "Joint":     st.session_state.joint_no if st.session_state.joint_no else "-",
            "Std":       standard,
            "Prc":       process,
            "k":         k,
            "HI":        round(HI, 3),
            "Result":    status,
            "V":         voltage,
            "A":         current,
            "L(mm)":     length,
            "T(s)":      time_s,
            "Min":       min_range,
            "Max":       max_range,
        }
        st.session_state.history.insert(0, new_entry)
        if len(st.session_state.history) > 50:
            st.session_state.history.pop()
        st.toast("저장되었습니다!", icon="✅")
        st.rerun()

with b_cols[2]:
    if st.session_state.history:
        csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="Export CSV",
            data=csv,
            file_name="HI_" + datetime.now().strftime("%m%d_%H%M") + ".csv",
            mime="text/csv"
        )
    else:
        st.button("Export CSV", disabled=True)

# ======================================================
# 5. Optional Info Fields
# ======================================================
st.write("")
st.markdown('<div class="section-title">Additional Info <span style="font-weight:400; font-size:13px; color:#888;">(선택 입력)</span></div>', unsafe_allow_html=True)

opt_col1, opt_col2 = st.columns(2)
with opt_col1:
    wps_no    = st.text_input("WPS No.", placeholder="예) WPS-001", key="wps_no")
with opt_col2:
    welder_no = st.text_input("Welder No.", placeholder="예) W-123", key="welder_no")

opt_col3, opt_col4 = st.columns(2)
with opt_col3:
    joint_no  = st.text_input("Joint No.", placeholder="예) J-01", key="joint_no")
with opt_col4:
    st.markdown("**Pass Type**")
    pass_type = st.radio("Pass Type", ["Root", "Fill", "Cap"], horizontal=True, label_visibility="collapsed", key="pass_type")

# ======================================================
# 6. 히스토리 테이블
# ======================================================
if st.session_state.history:
    st.markdown('<div class="section-title">Recent History (최근 50건)</div>', unsafe_allow_html=True)

    col_clear, _ = st.columns([1, 3])
    with col_clear:
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()

    df = pd.DataFrame(st.session_state.history)

    def highlight_result(val):
        if val == "PASS":
            return "background-color: #00cc44; color: white; font-weight: bold;"
        elif val == "FAIL":
            return "background-color: #ff7f00; color: white; font-weight: bold;"
        return ""

    styled_df = df.style.applymap(highlight_result, subset=["Result"])
    st.dataframe(styled_df, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
