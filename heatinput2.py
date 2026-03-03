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
    .header { display:flex; align-items:center; border-bottom:4px solid #FF7F00; padding-bottom:10px; margin-bottom:15px; }
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
    /* Selectbox 흰색 */
    [data-testid="stSelectbox"] > div > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div[data-baseweb="popover"] ul {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div[data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #f0f0f0 !important;
    }
    /* Browse files 버튼 흰색 */
    [data-testid="stFileUploader"] button {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        height: auto !important;
        min-height: unset !important;
        font-size: 13px !important;
        padding: 4px 10px !important;
    }
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
if 'preset_wps_no'  not in st.session_state: st.session_state.preset_wps_no  = ""


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

# -- Manual (사용법) --
if 'manual_open' not in st.session_state:
    st.session_state.manual_open = False
if 'manual_lang' not in st.session_state:
    st.session_state.manual_lang = "EN"

with st.expander("User Manual", expanded=st.session_state.manual_open):
    lang_col, _ = st.columns([1, 3])
    with lang_col:
        lang = st.radio("Language", ["EN", "KO"], horizontal=True,
                        index=0 if st.session_state.manual_lang == "EN" else 1,
                        label_visibility="collapsed")
        st.session_state.manual_lang = lang

    if lang == "EN":
        st.markdown("""
<div style="font-size:13px; line-height:1.9; color:#000; padding:4px;">
<b style="font-size:14px;">Heat Input Master(v.0.5) - User Manual</b><br><br>

<b>1. Standard / Process</b><br>
&nbsp;&nbsp;- Standard: AWS (k=1.0 fixed) / ISO (SAW=1.0, GMAW/FCAW/SMAW=0.8)<br>
&nbsp;&nbsp;- Process: Select welding process (SAW / FCAW / SMAW / GMAW)<br><br>

<b>2. WPS Range (kJ/mm)</b><br>
&nbsp;&nbsp;- <b>Manual</b>: Enter Min / Max directly for judgment<br>
&nbsp;&nbsp;- <b>Preset</b>: Select from pre-registered WPS list for judgment<br>
&nbsp;&nbsp;&nbsp;&nbsp;&#128194; (Import): Upload TXT file (tab-delimited format)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&#128196; (Sample): Download sample TXT, fill values, then Import<br>
&nbsp;&nbsp;&nbsp;&nbsp;View WPS List: Select WPS from list, click [Apply Selection]<br>
&nbsp;&nbsp;&nbsp;&nbsp;Before import, default data (WPS-001~005) is used<br>
&nbsp;&nbsp;- <b>Default</b>: Display heat input value only, no judgment<br><br>

<b>3. Input Parameters</b><br>
&nbsp;&nbsp;- Enter Volt(V) / Amp(A) / Len(mm) / Time(s)<br>
&nbsp;&nbsp;- Formula: HI = k x V x A x T / (L x 1000) [kJ/mm]<br><br>

<b>4. Live Result</b><br>
&nbsp;&nbsp;- Green PASS: Heat input is within WPS range<br>
&nbsp;&nbsp;- Orange FAIL: Heat input is out of WPS range<br>
&nbsp;&nbsp;- White (-): Default mode, no judgment<br><br>

<b>5. Optional Info</b><br>
&nbsp;&nbsp;- Enter WPS No. / Welder No. / Joint No. (included in saved data)<br>
&nbsp;&nbsp;- WPS No. is auto-filled when a Preset WPS is selected<br><br>

<b>6. Weld Pass</b><br>
&nbsp;&nbsp;- Select applicable pass: Root / Fill / Cap<br><br>

<b>7. Save Data / Export</b><br>
&nbsp;&nbsp;- Save Data: Save current result to history (max 50 records)<br>
&nbsp;&nbsp;- Export: Download saved data as CSV file<br>
&nbsp;&nbsp;- Save time is based on the local time of the accessing device<br><br>

<b>8. TXT Import File Format</b><br>
&nbsp;&nbsp;- Delimiter: Tab<br>
&nbsp;&nbsp;- Format: WPS_No [TAB] Pass [TAB] H/I Min. [TAB] H/I Max.<br>
&nbsp;&nbsp;- Lines starting with # are treated as comments / Max 20 rows
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="font-size:13px; line-height:1.9; color:#000; padding:4px;">
<b style="font-size:14px;">Heat Input Master(v.0.5) 사용법</b><br><br>

<b>1. Standard / Process</b><br>
&nbsp;&nbsp;- Standard: AWS(k=1.0 고정) / ISO(SAW=1.0, GMAW/FCAW/SMAW=0.8)<br>
&nbsp;&nbsp;- Process: 용접 공법 선택 (SAW / FCAW / SMAW / GMAW)<br><br>

<b>2. WPS Range (kJ/mm)</b><br>
&nbsp;&nbsp;- <b>Manual</b>: Min / Max 직접 입력하여 판정<br>
&nbsp;&nbsp;- <b>Preset</b>: 사전 등록된 WPS 목록에서 선택하여 판정<br>
&nbsp;&nbsp;&nbsp;&nbsp;&#128194; (Import): TXT 파일 업로드 (탭 구분자 형식)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&#128196; (Sample): Sample TXT 다운로드 &gt; 값 입력 후 Import<br>
&nbsp;&nbsp;&nbsp;&nbsp;View WPS List: 목록 선택 후 [선택 적용] 클릭<br>
&nbsp;&nbsp;&nbsp;&nbsp;Import 전에는 기본 데이터(WPS-001~005) 사용<br>
&nbsp;&nbsp;- <b>Default</b>: 판정 없이 열입력 값만 표시<br><br>

<b>3. Input Parameters</b><br>
&nbsp;&nbsp;- Volt(V) / Amp(A) / Len(mm) / Time(s) 입력<br>
&nbsp;&nbsp;- 계산식: HI = k x V x A x T / (L x 1000) [kJ/mm]<br><br>

<b>4. Live Result</b><br>
&nbsp;&nbsp;- 녹색 PASS: 열입력이 WPS 범위 내<br>
&nbsp;&nbsp;- 주황 FAIL: 열입력이 WPS 범위 초과 또는 미달<br>
&nbsp;&nbsp;- 흰색 (-): Default 모드 (판정 없음)<br><br>

<b>5. Optional Info</b><br>
&nbsp;&nbsp;- WPS No. / Welder No. / Joint No. 입력 (저장 데이터에 포함)<br>
&nbsp;&nbsp;- Preset 모드에서 WPS 선택시 WPS No. 자동 입력<br><br>

<b>6. Weld Pass</b><br>
&nbsp;&nbsp;- Root / Fill / Cap 중 해당 패스 선택<br><br>

<b>7. Save Data / Export</b><br>
&nbsp;&nbsp;- Save Data: 현재 결과를 히스토리에 저장 (최대 50건)<br>
&nbsp;&nbsp;- Export: 저장된 데이터를 CSV 파일로 다운로드<br>
&nbsp;&nbsp;- 저장 시간은 접속 기기의 로컬 시간 기준<br><br>

<b>8. TXT Import 파일 형식</b><br>
&nbsp;&nbsp;- 구분자: 탭(Tab)<br>
&nbsp;&nbsp;- 형식: WPS번호 [TAB] Pass [TAB] H/I Min. [TAB] H/I Max.<br>
&nbsp;&nbsp;- # 으로 시작하는 줄은 주석 처리 / 최대 20행
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Close", key="manual_close"):
        st.session_state.manual_open = False
        st.rerun()

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

    # View WPS List expander - 한 줄 selectbox 방식
    with st.expander("📋 View WPS List", expanded=st.session_state.expander_open):
        options = [f"{item['wps_no']}  {item['pass']}  {item['hi_min']} ~ {item['hi_max']}" for item in presets]
        selected_str = st.selectbox("WPS 선택", options, label_visibility="collapsed")
        if st.button("✔ 선택 적용"):
            idx = options.index(selected_str)
            item = presets[idx]
            st.session_state.preset_min    = item["hi_min"]
            st.session_state.preset_max    = item["hi_max"]
            st.session_state.preset_label  = f"{item['wps_no']} / {item['pass']}"
            st.session_state.preset_wps_no = item["wps_no"]
            st.session_state.expander_open = False
            st.rerun()

    min_range = st.session_state.preset_min
    max_range = st.session_state.preset_max

# Default: 판정 없음
if wps_mode != "Preset":
    st.session_state.preset_wps_no = ""


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
with opt_cols[0]: wps_no    = st.text_input("WPS No.",    value=st.session_state.get("preset_wps_no",""), placeholder="WPS No.")
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