import streamlit as st
import deepl
import requests
from PIL import Image
import io
import base64

st.set_page_config(page_title="통합 학사 번역기 | Multi-Engine Translator", page_icon="🌐", layout="centered")

# 세션 상태 초기화
if "started" not in st.session_state:
    st.session_state.started = False
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "한국어 (Korean)"

# ---------------------------------------------------------
# 1. 무료 구글 번역 직접 호출 함수 (POST 방식)
# ---------------------------------------------------------
def free_google_translate(text, target_lang_code):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": target_lang_code,
        "dt": "t"
    }
    data = {"q": text}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.post(url, params=params, data=data, headers=headers, timeout=10)
    response.raise_for_status()
    result = response.json()
    
    translated_sentences = []
    if result and isinstance(result, list) and len(result) > 0 and result[0]:
        for item in result[0]:
            if item and isinstance(item, list) and len(item) > 0 and item[0]:
                translated_sentences.append(item[0])
    
    translated_text = "".join(translated_sentences)
    return translated_text if translated_text else text

# ---------------------------------------------------------
# 2. 계정별 동작 가능한 모델을 자동 감지하는 Gemini REST 호출 함수
# ---------------------------------------------------------
def generate_gemini_auto(api_key, prompt, image=None):
    clean_key = api_key.strip()
    
    # 1단계: 내 API 키로 사용 가능한 Gemini 모델 목록 조회
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={clean_key}"
    valid_models = []
    
    try:
        list_res = requests.get(list_url, timeout=10)
        if list_res.status_code == 200:
            models_data = list_res.json().get("models", [])
            for m in models_data:
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    name = m.get("name", "")
                    if name:
                        valid_models.append(name)
    except Exception:
        pass

    # 계정 목록 조회가 실패하거나 비어있을 경우 대비한 하드코딩 백업
    if not valid_models:
        valid_models = [
            "models/gemini-1.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-pro",
            "models/gemini-1.0-pro"
        ]

    # 우선순위 정렬 (flash 계열 우선)
    valid_models.sort(key=lambda x: 0 if "flash" in x else 1)

    # 2단계: 이미지/텍스트 요청 페이로드 구성
    parts = [{"text": prompt}]
    if image:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img_str
            }
        })
        
    payload = {"contents": [{"parts": parts}]}
    headers = {"Content-Type": "application/json"}

    # 3단계: 확인된 사용 가능 모델 주소로 순차 호출
    last_err = ""
    for model_fullname in valid_models:
        # models/gemini-1.5-flash 형태로 들어오므로 그대로 URL 생성
        target_url = f"https://generativelanguage.googleapis.com/v1beta/{model_fullname}:generateContent?key={clean_key}"
        try:
            res = requests.post(target_url, json=payload, headers=headers, timeout=20)
            if res.status_code == 200:
                res_data = res.json()
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                last_err = f"[{model_fullname}] Code {res.status_code}: {res.text}"
        except Exception as e:
            last_err = str(e)
            continue

    raise RuntimeError(f"모든 Gemini 모델 호출 실패. (상세 에러: {last_err})")

# ---------------------------------------------------------
# 다국어 텍스트 사전
# ---------------------------------------------------------
TEXTS = {
    "한국어 (Korean)": {
        "title": "🌐 통합 학사 번역기 서비스",
        "subtitle": "환영합니다! 시작하기 전 기본 언어 설정과 가이드라인을 확인해 주세요.",
        "lang_label": "번역 결과로 출력될 언어를 선택하세요:",
        "guide_title": "📋 서비스 이용 가이드라인 및 안내",
        "guide_content": """
        ### 📌 서비스 개요 및 작동 방식
        본 번역기는 사용자의 편의와 번역 품질을 극대화하기 위해 **다중 엔진 연동 시스템**을 지원합니다.
        """,
        "start_btn": "🚀 설정 확인 및 번역기 시작하기",
        "sidebar_title": "⚙️ 엔진 설정 및 안내",
        "engine_select": "번역 엔진 선택",
        "api_input": "API Key 입력 (선택 사항)",
        "current_lang": "현재 설정된 목표 언어:",
        "back_btn": "🔄 첫 화면으로 돌아가기",
        "tab1": "📝 텍스트 번역",
        "tab2": "🖼️ 이미지 번역",
        "text_header": "텍스트 번역",
        "text_prompt": "번역할 텍스트를 입력하세요:",
        "text_btn": "텍스트 번역 실행",
        "img_header": "이미지 번역 (Gemini 전용)",
        "img_prompt": "이미지 파일을 업로드하세요 (PNG, JPG, JPEG)",
        "img_btn": "이미지 번역 실행",
        "warning_text": "⚠️ 번역할 텍스트를 입력해 주세요.",
        "spinner_text": "번역 진행 중입니다...",
        "spinner_img": "이미지 분석 및 번역 진행 중입니다...",
        "success_res": "✨ 번역 결과:",
        "success_img": "✨ 이미지 번역 결과:",
        "error_msg": "❌ 번역 중 에러가 발생했습니다: "
    },
    "영어 (English)": {
        "title": "🌐 Multi-Engine Academic Translator",
        "subtitle": "Welcome! Please review the guidelines before starting.",
        "lang_label": "Select the target output language for translation:",
        "guide_title": "📋 Service Guidelines & Instructions",
        "guide_content": """
        ### 📌 Service Overview & Operation
        This translator supports a **multi-engine system** to maximize convenience and quality.
        """,
        "start_btn": "🚀 Confirm Settings & Start Translator",
        "sidebar_title": "⚙️ Engine Settings & Info",
        "engine_select": "Select Translation Engine",
        "api_input": "API Key (Optional)",
        "current_lang": "Current Target Language:",
        "back_btn": "🔄 Return to Home",
        "tab1": "📝 Text Translation",
        "tab2": "🖼️ Image Translation",
        "text_header": "Text Translation",
        "text_prompt": "Enter text to translate:",
        "text_btn": "Run Text Translation",
        "img_header": "Image Translation (Gemini Only)",
        "img_prompt": "Upload image file (PNG, JPG, JPEG)",
        "img_btn": "Run Image Translation",
        "warning_text": "⚠️ Please enter text to translate.",
        "spinner_text": "Translating...",
        "spinner_img": "Analyzing and translating image...",
        "success_res": "✨ Translation Result:",
        "success_img": "✨ Image Translation Result:",
        "error_msg": "❌ An error occurred: "
    }
}

lang_choice = st.session_state.get("target_lang", "한국어 (Korean)")
t = TEXTS.get(lang_choice, TEXTS["한국어 (Korean)"])

# ---------------------------------------------------------
# [1단계] 메인 첫 화면
# ---------------------------------------------------------
if not st.session_state.started:
    st.title("🌐 스마트 학사 번역기")
    st.subheader("환영합니다! 언어 설정과 가이드라인을 확인해 주세요.")
    
    st.divider()

    selected_lang = st.selectbox(
        "번역 결과로 출력될 언어를 선택하세요:",
        list(TEXTS.keys()),
        index=list(TEXTS.keys()).index(st.session_state.target_lang) if st.session_state.target_lang in TEXTS else 0
    )
    
    if selected_lang != st.session_state.target_lang:
        st.session_state.target_lang = selected_lang
        st.rerun()

    st.divider()

    t_current = TEXTS[selected_lang]
    st.markdown(f"### {t_current['guide_title']}")
    st.info(t_current['guide_content'])

    st.divider()

    if st.button(t_current['start_btn'], use_container_width=True):
        st.session_state.started = True
        st.rerun()

# ---------------------------------------------------------
# [2단계] 메인 번역 화면
# ---------------------------------------------------------
else:
    st.title(t['title'])
    
    st.sidebar.title(t['sidebar_title'])
    engine_choice = st.sidebar.selectbox(t['engine_select'], ["기본 자동 기계번역 (키 불필요)", "Google Gemini", "DeepL"])
    api_key = st.sidebar.text_input(t['api_input'], type="password")
    
    st.sidebar.markdown(f"**현재 엔진:** `{engine_choice}`")
    st.sidebar.markdown(f"**{t['current_lang']}**\n`{st.session_state.target_lang}`")
    
    if st.sidebar.button(t['back_btn']):
        st.session_state.started = False
        st.rerun()

    st.divider()

    tab1, tab2 = st.tabs([t['tab1'], t['tab2']])

    lang_map = {
        "한국어 (Korean)": "ko",
        "영어 (English)": "en",
        "스페인어 (Spanish)": "es",
        "러시아어 (Russian)": "ru",
        "일본어 (Japanese)": "ja",
        "중국어 (Chinese)": "zh-CN",
        "프랑스어 (French)": "fr",
        "독일어 (German)": "de"
    }

    lang_name = st.session_state.target_lang
    target_code = lang_map.get(lang_name, "en")

    # --- [탭 1: 텍스트 번역] ---
    with tab1:
        st.header(t['text_header'])
        user_text = st.text_area(t['text_prompt'], height=180)
        
        if st.button(t['text_btn'], use_container_width=True):
            if not user_text.strip():
                st.warning(t['warning_text'])
            else:
                try:
                    if engine_choice == "DeepL" and api_key:
                        translator = deepl.Translator(api_key)
                        deepl_codes = {"한국어 (Korean)": "KO", "영어 (English)": "EN-US", "스페인어 (Spanish)": "ES", "러시아어 (Russian)": "RU", "일본어 (Japanese)": "JA"}
                        with st.spinner(t['spinner_text']):
                            result = translator.translate_text(user_text, target_lang=deepl_codes.get(lang_name, "EN-US"))
                        st.success(t['success_res'])
                        st.write(result.text)
                    
                    elif engine_choice == "Google Gemini" and api_key:
                        prompt = f"다음 텍스트를 오직 번역 결과만 깔끔하게 자연스럽고 정확하게 {lang_name}로 번역해줘:\n\n{user_text}"
                        with st.spinner(t['spinner_text']):
                            translated_res = generate_gemini_auto(api_key, prompt)
                        st.success(t['success_res'])
                        st.write(translated_res)
                        
                    else:
                        with st.spinner(t['spinner_text']):
                            translated_text = free_google_translate(user_text, target_code)

                        st.success(t['success_res'])
                        st.write(translated_text)
                        
                except Exception as e:
                    st.error(f"{t['error_msg']}{e}")

    # --- [탭 2: 이미지 번역] ---
    with tab2:
        st.header(t['img_header'])
        uploaded_file = st.file_uploader(t['img_prompt'], type=["png", "jpg", "jpeg"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            if st.button(t['img_btn'], use_container_width=True):
                if not api_key:
                    st.warning("⚠️ 이미지 분석 및 OCR 번역을 이용하려면 사이드바에 **Google Gemini API 키**를 입력해 주세요.")
                else:
                    try:
                        prompt = f"이 이미지 안에 들어있는 텍스트를 추출하고, 추출한 내용을 {lang_name}로 정확하고 자연스럽게 번역해줘. 결과는 [원문 텍스트]와 [번역 결과]로 나누어서 출력해줘."
                        
                        with st.spinner(t['spinner_img']):
                            translated_img_res = generate_gemini_auto(api_key, prompt, image)
                            
                        st.success(t['success_img'])
                        st.write(translated_img_res)
                    except Exception as e:
                        st.error(f"{t['error_msg']}{e}")
