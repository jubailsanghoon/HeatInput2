import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(
    layout="centered",
    page_title="Heat Input Master",
    page_icon="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg"
)

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
    [data-testid="stFileUploader"] {
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        padding: 4px !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
        border: 1px dashed #aaaaaa !important;
        padding: 6px !important;
        min-height: unset !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── 기본 Preset 데이터 ──
DEFAULT_PRESETS = [
    {"wps_no": "WPS-001", "pass": "Root", "hi_min": 0.80, "hi_max": 2.10},
    {"wps_no": "WPS-001", "pass": "Fill", "hi_min": 0.90, "hi_max": 2.00},
    {"wps_no": "WPS-001", "pass": "Cap",  "hi_min": 1.30, "hi_max": 3.10},
    {"wps_no": "WPS-002", "pass": "Root", "hi_min": 0.80, "hi_max": 3.20},
    {"wps_no": "WPS-002", "pass": "Fill", "hi_min": 0.90, "hi_max": 2.00},
    {"wps_no": "WPS-002", "pass": "Cap",  "hi_min": 0.90, "hi_max": 2.00},
    {"wps_no": "WPS-003", "pass": "Root", "hi_min": 0.90, "hi_max": 2.00},
    {"wps_no": "WPS-003", "pass": "Fill", "hi_min": 0.92, "hi_max": 2.00},
    {"wps_no": "WPS-003", "pass": "Cap",  "hi_min": 0.83, "hi_max": 2.00},
    {"wps_no": "WPS-004", "pass": "Root", "hi_min": 0.82, "hi_max": 3.20},
    {"wps_no": "WPS-004", "pass": "Fill", "hi_min": 0.78, "hi_max": 2.00},
    {"wps_no": "WPS-004", "pass": "Cap",  "hi_min": 0.80, "hi_max": 3.20},
    {"wps_no": "WPS-005", "pass": "Root", "hi_min": 0.67, "hi_max": 4.00},
    {"wps_no": "WPS-005", "pass": "Fill", "hi_min": 0.80, "hi_max": 3.20},
    {"wps_no": "WPS-005", "pass": "Cap",  "hi_min": 0.94, "hi_max": 3.00},
]

# ── 세션 상태 초기화 ──
if 'history'        not in st.session_state: st.session_state.history        = []
if 'wps_presets'    not in st.session_state: st.session_state.wps_presets    = None  # None = 기본값 사용
if 'preset_min'     not in st.session_state: st.session_state.preset_min     = None
if 'preset_max'     not in st.session_state: st.session_state.preset_max     = None
if 'preset_label'   not in st.session_state: st.session_state.preset_label   = ""
if 'show_import'    not in st.session_state: st.session_state.show_import    = False
if 'expander_open'  not in st.session_state: st.session_state.expander_open  = False

def get_presets():
    return st.session_state.wps_presets if st.session_state.wps_presets is not None else DEFAULT_PRESETS

# ── query_params 로컬 시간 ──
params     = st.query_params
local_time = params.get("localtime", "")
if not (local_time and len(local_time) == 8):
    local_time = datetime.now().strftime("%H:%M:%S")

# ── JS mousedown 리스너 ──
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
wps_mode = st.radio("WPS Mode", ["Manual", "Preset", "Default"], horizontal=True, label_visibility="collapsed")

min_range = None
max_range = None

if wps_mode == "Manual":
    w_cols = st.columns([0.5, 1.5, 0.5, 1.5])
    with w_cols[0]: st.markdown("**Min**")
    with w_cols[1]: min_range = st.number_input("min", value=0.96, step=0.01, format="%.2f", label_visibility="collapsed")
    with w_cols[2]: st.markdown("**Max**")
    with w_cols[3]: max_range = st.number_input("max", value=2.50, step=0.01, format="%.2f", label_visibility="collapsed")

elif wps_mode == "Preset":
    presets = get_presets()
    is_default = st.session_state.wps_presets is None

    # 📂 Import / 📄 Sample 아이콘 버튼
    ic1, ic2, ic3 = st.columns([0.12, 0.12, 0.76])
    with ic1:
        if st.button("📂", help="Import TXT"):
            st.session_state.show_import = not st.session_state.show_import
            st.rerun()
    with ic2:
        sample_lines = [
            "# WPS Preset - Heat Input Master",
            "# 형식: WPS번호\tPass\tH/I Min.\tH/I Max.",
            "# Pass: Root / Fill / Cap  |  최대 20행",
            "#",
        ]
        for item in DEFAULT_PRESETS:
            sample_lines.append(f"{item['wps_no']}\t{item['pass']}\t{item['hi_min']}\t{item['hi_max']}")
        sample_txt = "\n".join(sample_lines).encode('utf-8')
        st.download_button("📄", data=sample_txt,
                           file_name="WPS_sample.txt", mime="text/plain",
                           help="Sample TXT 다운로드")
    with ic3:
        src_label = "기본 데이터 사용 중" if is_default else f"업로드 데이터 사용 중 ({len(presets)}건)"
        st.caption(src_label)

    # 파일 업로더 (토글)
    if st.session_state.show_import:
        uploaded = st.file_uploader("TXT", type="txt", label_visibility="collapsed")
        if uploaded:
            try:
                lines = uploaded.read().decode('utf-8').splitlines()
                records = []
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split('\t')
                    if len(parts) != 4:
                        continue
                    wps_no, pass_, hi_min, hi_max = [p.strip() for p in parts]
                    records.append({"wps_no": wps_no, "pass": pass_,
                                    "hi_min": float(hi_min), "hi_max": float(hi_max)})
                    if len(records) >= 20:
                        break
                if records:
                    st.session_state.wps_presets   = records
                    st.session_state.show_import   = False
                    st.session_state.preset_label  = ""
                    st.session_state.preset_min    = None
                    st.session_state.preset_max    = None
                    st.success(f"{len(records)}개 WPS 로드 완료")
                    st.rerun()
                else:
                    st.error("데이터 없음. 형식: WPS번호[TAB]Pass[TAB]Min[TAB]Max")
            except Exception as e:
                st.error(f"파일 오류: {e}")

    # 현재 선택된 Preset 표시
    if st.session_state.preset_label:
        st.info(f"✔ {st.session_state.preset_label}  |  Min: {st.session_state.preset_min}  Max: {st.session_state.preset_max}")
    else:
        st.caption("아래 목록에서 WPS를 선택하세요")

    # View WPS List expander
    with st.expander("📋 View WPS List", expanded=st.session_state.expander_open):
        # 헤더
        h = st.columns([3, 2, 3, 1])
        h[0].markdown("**WPS No.**")
        h[1].markdown("**Pass**")
        h[2].markdown("**Min / Max**")
        h[3].markdown("**✔**")
        st.divider()
        for idx, item in enumerate(presets):
            r = st.columns([3, 2, 3, 1])
            r[0].write(item["wps_no"])
            r[1].write(item["pass"])
            r[2].write(f"{item['hi_min']} ~ {item['hi_max']}")
            if r[3].button("✔", key=f"sel_{idx}"):
                st.session_state.preset_min    = item["hi_min"]
                st.session_state.preset_max    = item["hi_max"]
                st.session_state.preset_label  = f"{item['wps_no']} / {item['pass']}"
                st.session_state.expander_open = False
                st.rerun()

    min_range = st.session_state.preset_min
    max_range = st.session_state.preset_max

# Default: 판정 없음

# 3. Input Parameters & Live Result
st.write("")
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)

    def draw_input_row(label, value, key):
        r_cols = st.columns([1.5, 2])
        with r_cols[0]: st.markdown(f"**{label}**")
        with r_cols[1]: return st.number_input(label, value=value, step=0.1, format="%.1f", key=key, label_visibility="collapsed")

    voltage = draw_input_row("Volt (V)",  30.0, "v")
    current = draw_input_row("Amp (A)", 300.0, "c")
    length  = draw_input_row("Len (mm)",   5.0, "l")
    time    = draw_input_row("Time (s)",   1.0, "t")

k  = 1.0 if standard == "AWS" else {"SAW": 1.0, "GMAW": 0.8, "FCAW": 0.8, "SMAW": 0.8}.get(process, 0.8)
HI = (k * voltage * current * time) / (length * 1000) if length > 0 else 0

if min_range is not None and max_range is not None:
    status = "PASS" if min_range <= HI <= max_range else "FAIL"
else:
    status = "-"

with col_right:
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    box_class = "result-box-pass" if status == "PASS" else ("result-box-fail" if status == "FAIL" else "result-box-none")
    st.markdown(
        f'<div class="{box_class}">{HI:.3f} kJ/mm<br><span style="font-size:14px;">{status}</span></div>',
        unsafe_allow_html=True
    )

# 4. Optional Info
st.markdown('<div class="section-title">Optional Info</div>', unsafe_allow_html=True)
opt_cols = st.columns(3)
with opt_cols[0]: wps_no    = st.text_input("WPS No.",    value="", placeholder="WPS No.")
with opt_cols[1]: welder_no = st.text_input("Welder No.", value="", placeholder="Welder No.")
with opt_cols[2]: joint_no  = st.text_input("Joint No.",  value="", placeholder="Joint No.")

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
        st.download_button(label="Export", data=csv,
                           file_name=f"HI_{datetime.now().strftime('%m%d_%H%M')}.csv",
                           mime="text/csv")
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