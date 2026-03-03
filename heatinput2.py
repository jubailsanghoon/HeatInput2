import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Heat Input Master", page_icon="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg")

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
    .header { display:flex; align-items:center; border-bottom:4px solid black; padding-bottom:10px; margin-bottom:15px; }
    .header img { height:40px; margin-right:10px; }
    .title { font-size:22px; font-weight:900; }
    .section-title { font-size:16px; font-weight:900; margin-top:12px; margin-bottom:8px; }
    .result-box-pass { font-size:18px; font-weight:900; padding:8px; background:#90ee90; border:2px solid black; border-radius:6px; text-align:center; margin-bottom:8px; color:black !important; line-height:1.4; }
    .result-box-fail { font-size:18px; font-weight:900; padding:8px; background:#ff7f00; border:2px solid black; border-radius:6px; text-align:center; margin-bottom:8px; color:white !important; line-height:1.4; }
    .result-box-none { font-size:18px; font-weight:900; padding:8px; background:#ffffff; border:2px solid black; border-radius:6px; text-align:center; margin-bottom:8px; color:black !important; line-height:1.4; }
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
</style>
""", unsafe_allow_html=True)

# ── 세션 상태 초기화 ──
if 'history' not in st.session_state:
    st.session_state.history = []

# ── query_params에서 로컬 시간 읽기 ──
params = st.query_params
local_time = params.get("localtime", "")
if not (local_time and len(local_time) == 8):
    local_time = datetime.now().strftime("%H:%M:%S")

# ── JS: Save Data 버튼에 mousedown 시 로컬 시간을 URL에 기록 ──
components.html("""
<script>
(function() {
    function attachListener() {
        const buttons = window.parent.document.querySelectorAll('button');
        for (let btn of buttons) {
            if (btn.innerText.trim() === 'Save Data' && !btn._timeListenerAttached) {
                btn._timeListenerAttached = true;
                btn.addEventListener('mousedown', function() {
                    const now = new Date();
                    const t = String(now.getHours()).padStart(2,'0') + ':'
                            + String(now.getMinutes()).padStart(2,'0') + ':'
                            + String(now.getSeconds()).padStart(2,'0');
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('localtime', t);
                    window.parent.history.replaceState({}, '', url);
                });
            }
        }
    }
    // DOM 변경 감지해서 버튼이 생길 때마다 리스너 부착
    const observer = new MutationObserver(attachListener);
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    attachListener();
})();
</script>
""", height=0)

# ── Header ──
st.markdown("""
<div class="header">
<img src="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg">
<div class="title">Heat Input Master(v.0.5)</div>
</div>
""", unsafe_allow_html=True)

# 1. Standard & Process
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS", "ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW", "FCAW", "SMAW", "GMAW"], horizontal=True, label_visibility="collapsed")

# 2. WPS Range
st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
wps_input_mode = st.radio("WPS Mode", ["Input", "No input"], horizontal=True, label_visibility="collapsed")

if wps_input_mode == "Input":
    w_cols = st.columns([0.5, 1.5, 0.5, 1.5])
    with w_cols[0]:
        st.markdown("**Min**")
    with w_cols[1]:
        min_range = st.number_input("min", value=0.96, step=0.01, format="%.2f", label_visibility="collapsed")
    with w_cols[2]:
        st.markdown("**Max**")
    with w_cols[3]:
        max_range = st.number_input("max", value=2.50, step=0.01, format="%.2f", label_visibility="collapsed")
else:
    min_range = None
    max_range = None

# 3. Input Parameters & Live Result
st.write("")
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)

    def draw_input_row(label, value, key):
        r_cols = st.columns([1.5, 2])
        with r_cols[0]:
            st.markdown(f"**{label}**")
        with r_cols[1]:
            return st.number_input(label, value=value, step=0.1, format="%.1f", key=key, label_visibility="collapsed")

    voltage = draw_input_row("Volt (V)", 30.0, "v")
    current = draw_input_row("Amp (A)", 300.0, "c")
    length  = draw_input_row("Len (mm)", 5.0, "l")
    time    = draw_input_row("Time (s)", 1.0, "t")

k = 1.0 if standard == "AWS" else {"SAW": 1.0, "GMAW": 0.8, "FCAW": 0.8, "SMAW": 0.8}.get(process, 0.8)
HI = (k * voltage * current * time) / (length * 1000) if length > 0 else 0

if min_range is not None and max_range is not None:
    status = "PASS" if min_range <= HI <= max_range else "FAIL"
else:
    status = "-"

with col_right:
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    if status == "PASS":
        box_class = "result-box-pass"
    elif status == "FAIL":
        box_class = "result-box-fail"
    else:
        box_class = "result-box-none"
    st.markdown(
        f'<div class="{box_class}">{HI:.3f} kJ/mm<br><span style="font-size:14px;">{status}</span></div>',
        unsafe_allow_html=True
    )

# 4. Optional Info
st.markdown('<div class="section-title">Optional Info</div>', unsafe_allow_html=True)
opt_cols = st.columns(3)
with opt_cols[0]:
    wps_no = st.text_input("WPS No.", value="", placeholder="WPS No.")
with opt_cols[1]:
    welder_no = st.text_input("Welder No.", value="", placeholder="Welder No.")
with opt_cols[2]:
    joint_no = st.text_input("Joint No.", value="", placeholder="Joint No.")

# 5. Weld Pass
st.markdown('<div class="section-title">Weld Pass</div>', unsafe_allow_html=True)
pass_type = st.radio("Pass", ["Root", "Fill", "Cap"], horizontal=True, label_visibility="collapsed")

# 6. Buttons
btn_left, btn_gap, btn_right = st.columns([0.475, 0.05, 0.475])

with btn_left:
    save_clicked = st.button("Save Data")

with btn_right:
    if st.session_state.history:
        csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Export",
            data=csv,
            file_name=f"HI_{datetime.now().strftime('%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    else:
        st.button("Export", disabled=True)

if save_clicked:
    new_entry = {
        "Time":       local_time,
        "Std":        standard,
        "Prc":        process,
        "HI":         round(HI, 3),
        "Res":        status,
        "V":          voltage,
        "A":          current,
        "L":          length,
        "T":          time,
        "WPS No.":    wps_no,
        "Welder No.": welder_no,
        "Joint No.":  joint_no,
        "Pass":       pass_type,
    }
    st.session_state.history.insert(0, new_entry)
    if len(st.session_state.history) > 50:
        st.session_state.history.pop()
    st.rerun()

# 7. History
if st.session_state.history:
    st.markdown('<div class="section-title">Recent History</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)