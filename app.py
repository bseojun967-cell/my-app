import streamlit as st
import google.generativeai as genai
import deepl
import requests
from PIL import Image

st.set_page_config(page_title="통합 학사 번역기 | Multi-Engine Translator", page_icon="🌐", layout="centered")

# 세션 상태 초기화
if "started" not in st.session_state:
    st.session_state.started = False
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "한국어 (Korean)"

# ---------------------------------------------------------
# 1. 안정적인 무료 구글 번역 직접 호출 함수 (requests POST 방식)
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
    
    # 응답 데이터 조립 (문단이 여러 개일 경우 모두 결합)
    translated_sentences = []
    if result and isinstance(result, list) and len(result) > 0 and result[0]:
        for item in result[0]:
            if item and isinstance(item, list) and len(item) > 0 and item[0]:
                translated_sentences.append(item[0])
    
    translated_text = "".join(translated_sentences)
    return translated_text if translated_text else text

# ---------------------------------------------------------
# 2. 최신 Gemini 모델 안전 호출 함수
# ---------------------------------------------------------
def generate_gemini_response(api_key, prompt, image=None):
    genai.configure(api_key=api_key)
    
    # 최신 지원 모델 우선순위 목록
    candidate_models = [
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    
    last_error = None
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            if image:
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = e
            continue
            
    raise last_error if last_error else RuntimeError("Gemini 모델 호출에 실패했습니다. API 키를 확인해 주세요.")

# ---------------------------------------------------------
# 다국어 텍스트 사전 (UI Localization Dictionary)
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

        ---

        #### 1. 🔑 API 키 연동에 따른 번역 품질 안내
        * **[기본 모드] API 키가 없는 경우**
          * 별도의 설정이나 키 입력 없이도 **기본 기계번역 엔진**이 즉시 작동하여 신속하게 텍스트 번역을 제공합니다.
        * **[프리미엄 모드] API 키가 있는 경우**
          * 사이드바에 **Google Gemini** API 키를 입력하면 고품질의 정밀 번역본을 활용하실 수 있습니다.

        #### 2. ⚙️ 지원 엔진별 특징
        * **Google Gemini:** 자연스러운 문맥 파악 및 **이미지 텍스트 추출(OCR) 번역**에 최적화되어 있습니다. ([API 키 발급처](https://aistudio.google.com/))
        * **기본 자동 번역:** 키 입력 없이 언제나 편리하게 이용할 수 있는 고성능 기계번역 엔진입니다.

        #### 3. 🖼️ 이미지 번역 이용 안내
        * 이미지 파일(PNG, JPG, JPEG) 속 텍스트 분석 및 번역 기능은 **Google Gemini 엔진** 선택 및 API 키 입력 후 이용하실 수 있습니다.
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

    # 표준 언어 코드 매핑
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
                    # 1) DeepL 선택 + 키 있을 때
                    if engine_choice == "DeepL" and api_key:
                        translator = deepl.Translator(api_key)
                        deepl_codes = {"한국어 (Korean)": "KO", "영어 (English)": "EN-US", "스페인어 (Spanish)": "ES", "러시아어 (Russian)": "RU", "일본어 (Japanese)": "JA"}
                        with st.spinner(t['spinner_text']):
                            result = translator.translate_text(user_text, target_lang=deepl_codes.get(lang_name, "EN-US"))
                        st.success(t['success_res'])
                        st.write(result.text)
                    
                    # 2) Gemini 선택 + 키 있을 때
                    elif engine_choice == "Google Gemini" and api_key:
                        prompt = f"다음 텍스트를 오직 번역 결과만 깔끔하게 자연스럽고 정확하게 {lang_name}로 번역해줘:\n\n{user_text}"
                        with st.spinner(t['spinner_text']):
                            translated_res = generate_gemini_response(api_key, prompt)
                        st.success(t['success_res'])
                        st.write(translated_res)
                        
                    # 3) 기본 자동 기계번역 (안정적인 direct POST 방식)
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
                            translated_img_res = generate_gemini_response(api_key, prompt, image)
                            
                        st.success(t['success_img'])
                        st.write(translated_img_res)
                    except Exception as e:
                        st.error(f"{t['error_msg']}{e}")