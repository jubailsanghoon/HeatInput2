import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="Heat Input Master", layout="centered")

# 세션 상태 초기화 (수동 입력과 버튼 동기화용)
params_init = {'v': 28.0, 'a': 220.0, 'l': 150.0, 't': 120.0}
for k, v in params_init.items():
    if k not in st.session_state:
        st.session_state[k] = v
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. CSS 정밀 시공 (소장님 레이아웃 100% 재현) ---
st.markdown("""
<style>
    /* 전체 배경 및 폭 고정 (모바일 최적화) */
    .stApp { background-color: #F2F2F2; max-width: 480px; margin: 0 auto; }
    * { color: #000000 !important; font-family: 'Inter', sans-serif; }

    /* [S1] Standard (ISO/AWS) 큰 글씨 시인성 */
    div[role="radiogroup"] { display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 12px !important; }
    div[role="radiogroup"] label {
        height: 75px !important; border: 3px solid #000 !important; background: #FFF !important;
        justify-content: center !important; border-radius: 8px !important;
    }
    div[role="radiogroup"] label[data-checked="true"] { background: #000 !important; }
    div[role="radiogroup"] label[data-checked="true"] p { color: #FFF !important; font-size: 2.2rem !important; font-weight: 900 !important; }
    div[role="radiogroup"] label p { font-size: 2.2rem !important; font-weight: 900 !important; letter-spacing: -1px; }

    /* 섹션 타이틀 */
    .section-title { font-size: 1.3rem; font-weight: 900; margin: 20px 0 10px 0; border-left: 8px solid #000; padding-left: 12px; }

    /* [S4] 파라미터 입력창 레이아웃 (Label - Minus - Input - Plus) */
    .param-row { display: flex; align-items: center; width: 100%; margin-bottom: 12px; }
    
    /* 증감 버튼 스타일 */
    .stButton button {
        width: 100% !important; height: 52px !important; 
        background-color: #E0E0E0 !important; color: #000 !important;
        font-size: 2rem !important; font-weight: bold !important;
        border: 2px solid #000 !important; border-radius: 4px !important;
        padding: 0 !important;
    }
    .stButton button:active { background-color: #000 !important; color: #FFF !important; }

    /* 숫자 입력창 (수동 입력 가능하도록 스타일링) */
    .stNumberInput input {
        height: 52px !important; font-size: 1.5rem !important; font-weight: 900 !important;
        text-align: center !important; border: 2px solid #000 !important; 
        background: #FFFFFF !important;
    }
    
    /* 결과 및 상태 배너 */
    .result-display { background: #FFF; border: 4px solid #000; height: 95px; display: flex; align-items: center; justify-content: center; font-size: 2.8rem; font-weight: 900; margin-top: 15px; }
    .status-banner { height: 65px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 900; border-radius: 6px; margin-top: 10px; border: 3px solid #000; color: #FFF !important; }

    /* 수동 입력 시 화살표 제거 */
    input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
</style>
""", unsafe_allow_html=True)

# --- 3. 헤더 영역 ---
logo_url = "https://raw.githubusercontent.com/jubailsanghoon/Heatinput/main/db65c0d39f36f2dddc248ea0bf2e4efc.jpg"
st.markdown(f"""
    <div style="border-bottom:6px solid #000; padding-bottom:10px; margin-bottom:20px;">
        <img src="{logo_url}" width="65">
        <span style="font-size:1.8rem; font-weight:900; margin-left:15px; letter-spacing:-1px;">Heat Input Master</span>
    </div>
""", unsafe_allow_html=True)

# --- 4. 메인 레이아웃 (순차 배치) ---

# [S1] Standard Selection
st.markdown('<div class="section-title">Standard</div>', unsafe_allow_html=True)
std_mode = st.radio("Std", ['ISO', 'AWS'], horizontal=True, label_visibility="collapsed")

# [S2] WPS Range (제한 해제 버전)
st.markdown('<div class="section-title">WPS Range (kJ/mm)</div>', unsafe_allow_html=True)
col_min, col_max = st.columns(2)
with col_min:
    w_min = st.number_input("Min", value=1.0, step=0.1, format="%.1f")
with col_max:
    w_max = st.number_input("Max", value=2.5, step=0.1, format="%.1f")

# [S3] Select Process (2x2 그리드 느낌)
st.markdown('<div class="section-title">Select Process</div>', unsafe_allow_html=True)
proc = st.radio("Proc", ['SAW', 'FCAW', 'SMAW', 'GMAW'], horizontal=True, label_visibility="collapsed")

# [S4] Input Parameters (핵심: 라벨 - 마이너스 - 입력 - 플러스)
st.markdown('<div class="section-title">Input Parameters</div>', unsafe_allow_html=True)

def build_param_row(label, key, step_val):
    # 컬럼 비율: 라벨(3.5) | －(1.5) | 입력창(3.5) | ＋(1.5)
    c_label, c_minus, c_input, c_plus = st.columns([3.5, 1.5, 3.5, 1.5])
    
    with c_label:
        st.markdown(f"<div style='padding-top:14px; font-weight:900; font-size:1.1rem;'>{label}</div>", unsafe_allow_html=True)
    
    with c_minus:
        if st.button("－", key=f"btn_m_{key}"):
            st.session_state[key] = round(st.session_state[key] - step_val, 2)
            st.rerun()
            
    with c_input:
        # 수동 입력 동기화 로직
        val = st.number_input(label, value=st.session_state[key], step=0.0, format="%.1f", label_visibility="collapsed", key=f"num_{key}")
        if val != st.session_state[key]:
            st.session_state[key] = val
        
    with c_plus:
        if st.button("＋", key=f"btn_p_{key}"):
            st.session_state[key] = round(st.session_state[key] + step_val, 2)
            st.rerun()

build_param_row("Voltage (V)", 'v', 0.5)
build_param_row("Amperage (A)", 'a', 5.0)
build_param_row("Length (mm)", 'l', 10.0)
build_param_row("Time (Sec)", 't', 1.0)

# --- 5. 결과 산출 및 저장 ---
# 열효율 계수(k) 자동 선정
k_val = 1.0 if std_mode == 'AWS' or proc == 'SAW' else 0.8

v, a, l, t = st.session_state.v, st.session_state.a, st.session_state.l, st.session_state.t
hi_result = (k_val * v * a * t) / (l * 1000) if l > 0 else 0
is_pass = w_min <= hi_result <= w_max

st.markdown('<div class="section-title">Live Result</div>', unsafe_allow_html=True)
st.markdown(f'<div class="result-display">{hi_result:.3f} kJ/mm</div>', unsafe_allow_html=True)

res_color = "#28A745" if is_pass else "#DC3545"
st.markdown(f'<div class="status-banner" style="background:{res_color};">{"PASS" if is_pass else "FAIL"}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("💾 SAVE LOG DATA", use_container_width=True):
    st.session_state.history.insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Std": std_mode, "Proc": proc, "HI": f"{hi_result:.3f}", "Status": "PASS" if is_pass else "FAIL"
    })
    st.toast("Saved!")

if st.session_state.history:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.table(pd.DataFrame(st.session_state.history).head(5))