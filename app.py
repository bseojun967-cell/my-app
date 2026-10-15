import streamlit as st
import google.generativeai as genai
import deepl
from deep_translator import GoogleTranslator, MyMemoryTranslator
from PIL import Image
import time

st.set_page_config(page_title="통합 학사 번역기 | Multi-Engine Translator", page_icon="🌐", layout="centered")

# 세션 상태 초기화
if "started" not in st.session_state:
    st.session_state.started = False
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "한국어 (Korean)"

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
          * 사이드바에 **Google Gemini** 또는 **DeepL** API 키를 입력하면, 각 AI 엔진의 고유 특성을 살린 **고품질의 정밀 번역본**을 추가로 활용하실 수 있습니다.

        #### 2. ⚙️ 지원 엔진별 특징
        * **Google Gemini:** 자연스러운 문맥 파악 및 **이미지 텍스트 추출(OCR) 번역**에 최적화되어 있습니다. ([API 키 발급처](https://aistudio.google.com/))
        * **DeepL:** 텍스트 전용 엔진으로, 기계번역 중에서도 가장 자연스럽고 매끄러운 학술/전문 문서 번역 품질을 자랑합니다.

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

    # GoogleTranslator 언어 코드 매핑
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
    
    # MyMemoryTranslator 전용 언어 코드 매핑 (국가 코드 포함)
    mymemory_lang_map = {
        "한국어 (Korean)": "ko-KR",
        "영어 (English)": "en-US",
        "스페인어 (Spanish)": "es-ES",
        "러시아어 (Russian)": "ru-RU",
        "일본어 (Japanese)": "ja-JP",
        "중국어 (Chinese)": "zh-CN",
        "프랑스어 (French)": "fr-FR",
        "독일어 (German)": "de-DE"
    }

    lang_name = st.session_state.target_lang
    target_code = lang_map.get(lang_name, "en")
    mymemory_code = mymemory_lang_map.get(lang_name, "en-US")

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
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"다음 텍스트를 오직 번역 결과만 깔끔하게 자연스럽고 정확하게 {lang_name}로 번역해줘:\n\n{user_text}"
                        with st.spinner(t['spinner_text']):
                            response = model.generate_content(prompt)
                        st.success(t['success_res'])
                        st.write(response.text)
                        
                    # 3) 기본 자동 기계번역 (구글 차단 대비 예외 처리 및 우회 코드 보장)
                    else:
                        with st.spinner(t['spinner_text']):
                            time.sleep(0.3)
                            try:
                                translated_text = GoogleTranslator(source='auto', target=target_code).translate(user_text)
                            except Exception:
                                time.sleep(1.2)
                                try:
                                    translated_text = GoogleTranslator(source='auto', target=target_code).translate(user_text)
                                except Exception:
                                    # MyMemory 전용 규격(ko-KR) 코드 적용
                                    translated_text = MyMemoryTranslator(source='auto', target=mymemory_code).translate(user_text)

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
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"이 이미지 안에 들어있는 텍스트를 추출하고, 추출한 내용을 {lang_name}로 정확하고 자연스럽게 번역해줘. 결과는 [원문 텍스트]와 [번역 결과]로 나누어서 출력해줘."
                        
                        with st.spinner(t['spinner_img']):
                            response = model.generate_content([prompt, image])
                            
                        st.success(t['success_img'])
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"{t['error_msg']}{e}")