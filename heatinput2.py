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
    [data-testid="stAppViewContainer"], .stApp { background-color:#FFFFFF !important; color:#000000 !important; }
    h1,h2,h3,p,span,div,label,.stMarkdown { color:#000000 !important; }
    .header { display:flex; align-items:center; border-bottom:4px solid #FF7F00; padding-bottom:10px; margin-bottom:15px; }
    .header img { height:40px; margin-right:10px; }
    .title { font-size:22px; font-weight:900; }
    .section-title { font-size:16px; font-weight:900; margin-top:12px; margin-bottom:8px; }
    .result-box-pass { font-size:18px; font-weight:900; padding:8px; background:#90ee90; border:2px solid black; border-radius:6px; text-align:center; margin-bottom:8px; color:black !important; line-height:1.4; }
    .result-box-fail { font-size:18px; font-weight:900; padding:8px; background:#ff7f00; border:2px solid black; border-radius:6px; text-align:center; margin-bottom:8px; color:white !important; line-height:1.4; }
    .result-box-none { font-size:18px; font-weight:900; padding:8px; background:#ffffff; border:2px solid black; border-radius:6px; text-align:center; margin-bottom:8px; color:black !important; line-height:1.4; }
    .stButton > button, .stDownloadButton > button { width:100% !important; height:60px !important; font-size:16px !important; font-weight:900 !important; background-color:#f0f0f0 !important; color:black !important; border:2px solid black !important; border-radius:4px !important; margin-top:5px; }
    input { background-color:#ffffff !important; color:#000000 !important; border:1px solid #cccccc !important; }
    div[data-testid="stHorizontalBlock"] { align-items:center; gap:0.5rem; }
    .panel-box { border:1px solid #cccccc; border-radius:8px; padding:12px 16px; margin:6px 0 10px 0; background:#fafafa; }
    .disclaimer { font-size:13px; background:#fff8e1; border:1px solid #ffc107; border-radius:6px; padding:8px 12px; margin-bottom:10px; color:#000; }
    [data-testid="stSelectbox"] > div > div, div[data-baseweb="select"] > div { background-color:#ffffff !important; color:#000000 !important; }
    div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li { background-color:#ffffff !important; color:#000000 !important; }
    div[data-baseweb="popover"] li:hover { background-color:#f0f0f0 !important; }
    [data-testid="stFileUploader"] { background-color:#ffffff !important; border:1px solid #cccccc !important; border-radius:6px !important; padding:4px !important; }
    [data-testid="stFileUploader"] section { background-color:#ffffff !important; border:1px dashed #aaaaaa !important; padding:6px !important; min-height:unset !important; }
    [data-testid="stFileUploaderDropzoneInstructions"] { display:none !important; }
    [data-testid="stFileUploader"] button { background-color:#f0f0f0 !important; color:#000000 !important; border:1px solid #cccccc !important; height:auto !important; font-size:13px !important; padding:4px 10px !important; }
</style>
""", unsafe_allow_html=True)

DEFAULT_PRESETS = [
    {"wps_no":"WPS-001","pass":"Root","hi_min":0.80,"hi_max":2.10},
    {"wps_no":"WPS-001","pass":"Fill","hi_min":0.90,"hi_max":2.00},
    {"wps_no":"WPS-001","pass":"Cap", "hi_min":1.30,"hi_max":3.10},
    {"wps_no":"WPS-002","pass":"Root","hi_min":0.80,"hi_max":3.20},
    {"wps_no":"WPS-002","pass":"Fill","hi_min":0.90,"hi_max":2.00},
    {"wps_no":"WPS-002","pass":"Cap", "hi_min":0.90,"hi_max":2.00},
    {"wps_no":"WPS-003","pass":"Root","hi_min":0.90,"hi_max":2.00},
    {"wps_no":"WPS-003","pass":"Fill","hi_min":0.92,"hi_max":2.00},
    {"wps_no":"WPS-003","pass":"Cap", "hi_min":0.83,"hi_max":2.00},
    {"wps_no":"WPS-004","pass":"Root","hi_min":0.82,"hi_max":3.20},
    {"wps_no":"WPS-004","pass":"Fill","hi_min":0.78,"hi_max":2.00},
    {"wps_no":"WPS-004","pass":"Cap", "hi_min":0.80,"hi_max":3.20},
    {"wps_no":"WPS-005","pass":"Root","hi_min":0.67,"hi_max":4.00},
    {"wps_no":"WPS-005","pass":"Fill","hi_min":0.80,"hi_max":3.20},
    {"wps_no":"WPS-005","pass":"Cap", "hi_min":0.94,"hi_max":3.00},
]

DEFAULT_WELDERS = [
    {"welder_no":"Welder001","name":"Hong Gil-dong",  "dept":"Welding Dept."},
    {"welder_no":"Welder002","name":"Park Moon-su",   "dept":"Welding Dept."},
    {"welder_no":"Welder003","name":"Im Kkeok-jeong", "dept":"Welding Dept."},
]

DEFAULTS = {
    'history': [],
    'wps_presets': None,
    'preset_min': None,
    'preset_max': None,
    'preset_label': "",
    'show_import': False,
    'preset_wps_no': "",
    'welder_presets': None,
    'show_welder_import': False,
    'preset_welder_no': "",
    'preset_welder_name': "",
    'show_manual': False,
    'show_wps_list': False,
    'show_welder_list': False,
    'manual_lang': "EN",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def get_presets():
    return st.session_state.wps_presets if st.session_state.wps_presets is not None else DEFAULT_PRESETS

def get_welders():
    return st.session_state.welder_presets if st.session_state.welder_presets is not None else DEFAULT_WELDERS

local_time = st.query_params.get("localtime", "")
if not (local_time and len(local_time) == 8):
    local_time = datetime.now().strftime("%H:%M:%S")

components.html("""
<script>
(function(){
    function attach(){
        const btns=window.parent.document.querySelectorAll('button');
        for(let b of btns){
            if(b.innerText.trim()==='Save Data'&&!b._t){
                b._t=true;
                b.addEventListener('mousedown',function(){
                    const n=new Date();
                    const t=String(n.getHours()).padStart(2,'0')+':'+String(n.getMinutes()).padStart(2,'0')+':'+String(n.getSeconds()).padStart(2,'0');
                    const u=new URL(window.parent.location.href);
                    u.searchParams.set('localtime',t);
                    window.parent.history.replaceState({},'',u);
                });
            }
        }
    }
    new MutationObserver(attach).observe(window.parent.document.body,{childList:true,subtree:true});
    attach();
})();
</script>
""", height=0)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
<img src="https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg">
<div class="title">Heat Input Master (v.0.5)</div>
</div>
""", unsafe_allow_html=True)

# ─── User Manual ─────────────────────────────────────────────────────────────
if st.button("📖 User Manual  ▼" if not st.session_state.show_manual else "📖 User Manual  ▲",
             key="manual_toggle"):
    st.session_state.show_manual = not st.session_state.show_manual
    st.rerun()

if st.session_state.show_manual:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)

    lc, _ = st.columns([1, 3])
    with lc:
        new_lang = st.radio("lang", ["EN", "KO"], horizontal=True,
                            index=0 if st.session_state.manual_lang == "EN" else 1,
                            label_visibility="collapsed", key="lang_radio")
        if new_lang != st.session_state.manual_lang:
            st.session_state.manual_lang = new_lang
            st.rerun()

    cur_lang = st.session_state.manual_lang

    if cur_lang == "EN":
        st.markdown('<div class="disclaimer">⚠️ This app was created for personal use and may be modified, changed, or deleted without prior notice.</div>', unsafe_allow_html=True)
        st.markdown("""<div style="font-size:13px;line-height:1.9;color:#000;">
<b style="font-size:14px;">Heat Input Master (v.0.5) - User Manual</b><br><br>
<b>1. Standard / Process</b><br>
&nbsp;&nbsp;- AWS: k=1.0 fixed &nbsp;/&nbsp; ISO: SAW=1.0, GMAW/FCAW/SMAW=0.8<br>
&nbsp;&nbsp;- Process: SAW / FCAW / SMAW / GMAW<br><br>
<b>2. WPS Range (kJ/mm)</b><br>
&nbsp;&nbsp;- <b>Manual</b> (default): enter Min / Max directly<br>
&nbsp;&nbsp;- <b>Preset</b>: select from WPS list &nbsp;(📂 Import &nbsp;/&nbsp; ⬇️ Sample &nbsp;/&nbsp; View WPS List)<br>
&nbsp;&nbsp;&nbsp;&nbsp;Default data WPS-001~005 used before import<br>
&nbsp;&nbsp;- <b>Default</b>: no judgment, value only<br><br>
<b>3. Input Parameters</b><br>
&nbsp;&nbsp;- Volt (V) / Amp (A) / Len (mm) / Time (s)<br>
&nbsp;&nbsp;- HI = k × V × A × T / (L × 1000) &nbsp; kJ/mm<br><br>
<b>4. Live Result</b>: &nbsp;🟢 PASS &nbsp;/&nbsp; 🟠 FAIL &nbsp;/&nbsp; ⬜ No judgment<br><br>
<b>5. Optional Info</b><br>
&nbsp;&nbsp;- <b>Welder No.</b>: auto-filled when selected from Welder List (default: Manual input)<br>
&nbsp;&nbsp;- <b>WPS No.</b>: auto-filled from Preset WPS selection<br>
&nbsp;&nbsp;- <b>Joint No.</b>: manual entry &nbsp;&nbsp; <b>Dep't</b>: manual entry<br>
&nbsp;&nbsp;- Welder TXT format: Welder_No [TAB] Name [TAB] Dept &nbsp;(max 10 rows)<br><br>
<b>6. Weld Pass</b>: Root / Fill / Cap<br><br>
<b>7. Save Data / Export</b><br>
&nbsp;&nbsp;- Max <b>10 records</b> &nbsp;/&nbsp; CSV download &nbsp;/&nbsp; Local device time<br>
&nbsp;&nbsp;- Export filename: &nbsp;<i>HeatInput Record - MMDD-HHMM.csv</i><br><br>
<b>8. TXT File Format</b><br>
&nbsp;&nbsp;- WPS TXT: &nbsp;WPS_No [TAB] Pass [TAB] H/I Min. [TAB] H/I Max. &nbsp;(max 20 rows)<br>
&nbsp;&nbsp;- Welder TXT: &nbsp;Welder_No [TAB] Name [TAB] Dept &nbsp;(max 10 rows)<br>
&nbsp;&nbsp;- Lines starting with # are treated as comments
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="disclaimer">⚠️ 이 앱은 개인의 필요에 따라 작성되었으며 예고없이 수정, 변경, 삭제될 수 있습니다.</div>', unsafe_allow_html=True)
        st.markdown("""<div style="font-size:13px;line-height:1.9;color:#000;">
<b style="font-size:14px;">Heat Input Master (v.0.5) 사용법</b><br><br>
<b>1. Standard / Process</b><br>
&nbsp;&nbsp;- AWS: k=1.0 고정 &nbsp;/&nbsp; ISO: SAW=1.0, GMAW/FCAW/SMAW=0.8<br>
&nbsp;&nbsp;- Process: SAW / FCAW / SMAW / GMAW<br><br>
<b>2. WPS Range (kJ/mm)</b><br>
&nbsp;&nbsp;- <b>Manual</b> (기본값): Min/Max 직접 입력<br>
&nbsp;&nbsp;- <b>Preset</b>: WPS 목록에서 선택 &nbsp;(📂 Import &nbsp;/&nbsp; ⬇️ Sample &nbsp;/&nbsp; View WPS List)<br>
&nbsp;&nbsp;&nbsp;&nbsp;Import 전 기본 데이터 WPS-001~005 사용<br>
&nbsp;&nbsp;- <b>Default</b>: 판정 없이 값만 표시<br><br>
<b>3. Input Parameters</b><br>
&nbsp;&nbsp;- Volt (V) / Amp (A) / Len (mm) / Time (s)<br>
&nbsp;&nbsp;- HI = k × V × A × T / (L × 1000) &nbsp; kJ/mm<br><br>
<b>4. Live Result</b>: &nbsp;🟢 PASS &nbsp;/&nbsp; 🟠 FAIL &nbsp;/&nbsp; ⬜ 판정없음<br><br>
<b>5. Optional Info</b><br>
&nbsp;&nbsp;- <b>Welder No.</b>: Welder 목록 선택시 자동 입력 (기본값: 수동 입력)<br>
&nbsp;&nbsp;- <b>WPS No.</b>: Preset WPS 선택시 자동 입력<br>
&nbsp;&nbsp;- <b>Joint No.</b>: 직접 입력 &nbsp;&nbsp; <b>Dep't</b>: 직접 입력<br>
&nbsp;&nbsp;- Welder TXT 형식: Welder_No [TAB] 이름 [TAB] 부서 (최대 10행)<br><br>
<b>6. Weld Pass</b>: Root / Fill / Cap<br><br>
<b>7. Save Data / Export</b><br>
&nbsp;&nbsp;- 최대 <b>10건</b> &nbsp;/&nbsp; CSV 다운로드 &nbsp;/&nbsp; 기기 로컬 시간 기준<br>
&nbsp;&nbsp;- Export 파일명: &nbsp;<i>HeatInput Record - MMDD-HHMM.csv</i><br><br>
<b>8. TXT 파일 형식</b><br>
&nbsp;&nbsp;- WPS TXT: &nbsp;WPS번호 [TAB] Pass [TAB] H/I Min. [TAB] H/I Max. (최대 20행)<br>
&nbsp;&nbsp;- Welder TXT: &nbsp;Welder번호 [TAB] 이름 [TAB] 부서 (최대 10행)<br>
&nbsp;&nbsp;- # 으로 시작하는 줄은 주석 처리
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("✖ Close Manual", key="btn_close_manual"):
        st.session_state.show_manual = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─── 1. Standard & Process ───────────────────────────────────────────────────
c_std, c_prc = st.columns([1, 1])
with c_std:
    st.markdown('<div class="section-title">Standard</div>', unsafe_allow_html=True)
    standard = st.radio("Std", ["AWS","ISO"], horizontal=True, label_visibility="collapsed")
with c_prc:
    st.markdown('<div class="section-title">Process</div>', unsafe_allow_html=True)
    process = st.radio("Prc", ["SAW","FCAW","SMAW","GMAW"], horizontal=True, label_visibility="collapsed")

# ─── 2. WPS Range ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
wps_mode = st.radio("WPS Mode", ["Manual","Preset","Default"],
                    horizontal=True, label_visibility="collapsed", index=0)

min_range = None
max_range = None

if wps_mode == "Manual":
    wc = st.columns([0.5, 1.5, 0.5, 1.5])
    with wc[0]: st.markdown("**Min**")
    with wc[1]: min_range = st.number_input("min", value=0.96, step=0.01, format="%.2f", label_visibility="collapsed")
    with wc[2]: st.markdown("**Max**")
    with wc[3]: max_range = st.number_input("max", value=2.50, step=0.01, format="%.2f", label_visibility="collapsed")

elif wps_mode == "Preset":
    presets = get_presets()

    # 📂 and ⬇️ side by side
    ic1, ic2, ic3 = st.columns([0.09, 0.09, 0.82])
    with ic1:
        if st.button("📂", key="wps_imp_btn", help="Import WPS TXT"):
            st.session_state.show_import = not st.session_state.show_import
            st.rerun()
    with ic2:
        sl = ["# WPS Preset", "# No\tPass\tMin\tMax", "#"]
        for item in DEFAULT_PRESETS:
            sl.append(f"{item['wps_no']}\t{item['pass']}\t{item['hi_min']}\t{item['hi_max']}")
        st.download_button("⬇️", data="\n".join(sl).encode('utf-8'),
                           file_name="WPS_sample.txt", mime="text/plain",
                           help="Download WPS Sample TXT", key="wps_dl_btn")
    with ic3:
        st.caption("Default Data" if st.session_state.wps_presets is None
                   else f"Uploaded Data ({len(presets)} records)")

    if st.session_state.show_import:
        up = st.file_uploader("WPS TXT", type="txt", label_visibility="collapsed", key="wps_up")
        if up:
            try:
                recs = []
                for line in up.read().decode('utf-8').splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    p = line.split('\t')
                    if len(p) != 4: continue
                    recs.append({"wps_no":p[0].strip(),"pass":p[1].strip(),
                                 "hi_min":float(p[2]),"hi_max":float(p[3])})
                    if len(recs) >= 20: break
                if recs:
                    st.session_state.wps_presets = recs
                    st.session_state.show_import = False
                    st.session_state.preset_label = ""
                    st.session_state.preset_min = None
                    st.session_state.preset_max = None
                    st.success(f"{len(recs)} WPS records loaded.")
                    st.rerun()
                else:
                    st.error("No data found.")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.preset_label:
        st.info(f"Selected: {st.session_state.preset_label}  |  {st.session_state.preset_min} ~ {st.session_state.preset_max}")
    else:
        st.caption("Select WPS from the list below")

    # Toggle button for WPS list panel
    wps_list_label = ("▲ Hide WPS List" if st.session_state.show_wps_list else "▼ View WPS List")
    if st.button(wps_list_label, key="wps_list_toggle"):
        st.session_state.show_wps_list = not st.session_state.show_wps_list
        st.rerun()

    if st.session_state.show_wps_list:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        wps_opts = [f"{x['wps_no']} | {x['pass']} | {x['hi_min']} ~ {x['hi_max']}" for x in presets]
        wps_sel = st.selectbox("WPS", wps_opts, label_visibility="collapsed", key="wps_sel_box")
        bc1, bc2 = st.columns([1, 1])
        with bc1:
            if st.button("✔ Apply WPS", key="wps_apply"):
                i = wps_opts.index(wps_sel)
                st.session_state.preset_min = presets[i]["hi_min"]
                st.session_state.preset_max = presets[i]["hi_max"]
                st.session_state.preset_label = f"{presets[i]['wps_no']} / {presets[i]['pass']}"
                st.session_state.preset_wps_no = presets[i]["wps_no"]
                st.session_state.show_wps_list = False
                st.rerun()
        with bc2:
            if st.button("✖ Close WPS List", key="btn_close_wps"):
                st.session_state.show_wps_list = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    min_range = st.session_state.preset_min
    max_range = st.session_state.preset_max

if wps_mode != "Preset":
    st.session_state.preset_wps_no = ""

# ─── 3. Input Parameters & Live Result ───────────────────────────────────────
st.write("")
col_left, col_right = st.columns([1.2, 1])
with col_left:
    st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)
    def draw_input_row(label, value, key):
        rc = st.columns([1.5, 2])
        with rc[0]: st.markdown(f"**{label}**")
        with rc[1]: return st.number_input(label, value=value, step=0.1, format="%.1f",
                                            key=key, label_visibility="collapsed")
    voltage = draw_input_row("Volt (V)", 30.0, "v")
    current = draw_input_row("Amp (A)", 300.0, "c")
    length  = draw_input_row("Len (mm)", 5.0, "l")
    time_s  = draw_input_row("Time (s)", 1.0, "t")

k  = 1.0 if standard == "AWS" else {"SAW":1.0,"GMAW":0.8,"FCAW":0.8,"SMAW":0.8}.get(process, 0.8)
HI = (k * voltage * current * time_s) / (length * 1000) if length > 0 else 0
status = ("PASS" if (min_range is not None and max_range is not None and min_range <= HI <= max_range)
          else ("FAIL" if (min_range is not None and max_range is not None) else "-"))

with col_right:
    st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
    bc = "result-box-pass" if status == "PASS" else ("result-box-fail" if status == "FAIL" else "result-box-none")
    st.markdown(f'<div class="{bc}">{HI:.3f} kJ/mm<br><span style="font-size:14px;">{status}</span></div>',
                unsafe_allow_html=True)

# ─── 4. Optional Info ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Optional Info</div>', unsafe_allow_html=True)

welders = get_welders()

# 📂 and ⬇️ side by side
wi1, wi2, wi3 = st.columns([0.09, 0.09, 0.82])
with wi1:
    if st.button("📂", help="Import Welder TXT", key="wld_imp_btn"):
        st.session_state.show_welder_import = not st.session_state.show_welder_import
        st.rerun()
with wi2:
    wl = ["# Welder List", "# Welder_No\tName\tDept", "#"]
    for w in DEFAULT_WELDERS:
        wl.append(f"{w['welder_no']}\t{w['name']}\t{w.get('dept','')}")
    st.download_button("⬇️", data="\n".join(wl).encode('utf-8'),
                       file_name="Welder_sample.txt", mime="text/plain",
                       help="Download Welder Sample TXT", key="wld_dl_btn")
with wi3:
    st.caption("Default Welder Data" if st.session_state.welder_presets is None
               else f"Uploaded Welder Data ({len(welders)} records)")

if st.session_state.show_welder_import:
    wup = st.file_uploader("Welder TXT", type="txt", label_visibility="collapsed", key="wld_up")
    if wup:
        try:
            wrecs = []
            for line in wup.read().decode('utf-8').splitlines():
                line = line.strip()
                if not line or line.startswith('#'): continue
                p = line.split('\t')
                if len(p) < 2: continue
                dept = p[2].strip() if len(p) >= 3 else ""
                wrecs.append({"welder_no":p[0].strip(),"name":p[1].strip(),"dept":dept})
                if len(wrecs) >= 10: break
            if wrecs:
                st.session_state.welder_presets = wrecs
                st.session_state.show_welder_import = False
                st.session_state.preset_welder_no = ""
                st.session_state.preset_welder_name = ""
                st.success(f"{len(wrecs)} welders loaded.")
                st.rerun()
            else:
                st.error("No data found.")
        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.preset_welder_no:
    nm = st.session_state.preset_welder_name
    label_txt = (f"Selected Welder: {st.session_state.preset_welder_no}-{nm}" if nm
                 else f"Selected Welder: {st.session_state.preset_welder_no}")
    st.info(label_txt)
else:
    st.caption("Select Welder from list below (or enter manually)")

# Toggle button for Welder list panel
wld_list_label = ("▲ Hide Welder List" if st.session_state.show_welder_list else "▼ View Welder List")
if st.button(wld_list_label, key="wld_list_toggle"):
    st.session_state.show_welder_list = not st.session_state.show_welder_list
    st.rerun()

if st.session_state.show_welder_list:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    wld_opts = [f"{w['welder_no']} | {w['name']} | {w.get('dept','')}" for w in welders]
    wld_sel = st.selectbox("Welder", wld_opts, label_visibility="collapsed", key="wld_sel_box")
    wc1, wc2 = st.columns([1, 1])
    with wc1:
        if st.button("✔ Apply Welder", key="wld_apply"):
            i = wld_opts.index(wld_sel)
            st.session_state.preset_welder_no = welders[i]["welder_no"]
            st.session_state.preset_welder_name = welders[i]["name"]
            st.session_state.show_welder_list = False
            st.rerun()
    with wc2:
        if st.button("✖ Close Welder List", key="btn_close_wld"):
            st.session_state.show_welder_list = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 4 input columns
opt_cols = st.columns(4)
with opt_cols[0]:
    welder_no = st.text_input("Welder No.", value=st.session_state.get("preset_welder_no",""),
                               placeholder="Welder No.")
with opt_cols[1]:
    wps_no = st.text_input("WPS No.", value=st.session_state.get("preset_wps_no",""),
                            placeholder="WPS No.")
with opt_cols[2]:
    joint_no = st.text_input("Joint No.", value="", placeholder="Joint No.")
with opt_cols[3]:
    dept = st.text_input("Dep't", value="", placeholder="Dep't")

# ─── 5. Weld Pass ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Weld Pass</div>', unsafe_allow_html=True)
pass_type = st.radio("Pass", ["Root","Fill","Cap"], horizontal=True, label_visibility="collapsed")

# ─── 6. Save / Export ────────────────────────────────────────────────────────
bl, bg, br = st.columns([0.475, 0.05, 0.475])
with bl:
    save_clicked = st.button("Save Data")
with br:
    if st.session_state.history:
        csv_data = pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8-sig')
        now = datetime.now()
        fname = f"HeatInput Record - {now.strftime('%m%d')}-{now.strftime('%H%M')}.csv"
        st.download_button("Export", data=csv_data, file_name=fname, mime="text/csv")
    else:
        st.button("Export", disabled=True)

if save_clicked:
    if len(st.session_state.history) >= 10:
        st.warning("⚠️ Maximum 10 records reached. Please export before saving more.")
    else:
        st.session_state.history.insert(0, {
            "Time": local_time, "Std": standard, "Prc": process,
            "HI": round(HI, 3), "Res": status,
            "V": voltage, "A": current, "L": length, "T": time_s,
            "WPS No.": wps_no, "Welder No.": welder_no,
            "Joint No.": joint_no, "Dep't": dept, "Pass": pass_type,
        })
        st.rerun()

# ─── 7. History ──────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown('<div class="section-title">Recent History</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)