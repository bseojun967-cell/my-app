import streamlit as st
import deepl
import requests
from PIL import Image
import io
import base64
from datetime import datetime
import re

st.set_page_config(page_title="통합 학사 번역기 | Multi-Engine Translator", page_icon="🌐", layout="wide")

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
# 2. 계정별 동작 가능한 모델을 자동 감지하는 Gemini REST 호출 함수 (RGBA 에러 패치 적용 완료)
# ---------------------------------------------------------
def generate_gemini_auto(api_key, prompt, image=None):
    clean_key = api_key.strip()
    
    list_url = "https://generativelanguage.googleapis.com/v1beta/models?key=" + clean_key
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

    if not valid_models:
        valid_models = [
            "models/gemini-2.5-flash",
            "models/gemini-1.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-pro"
        ]

    valid_models.sort(key=lambda x: 0 if "flash" in x else 1)

    parts = [{"text": prompt}]
    if image:
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
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

    last_err = ""
    for model_fullname in valid_models:
        target_url = "https://generativelanguage.googleapis.com/v1beta/" + model_fullname + ":generateContent?key=" + clean_key
        try:
            res = requests.post(target_url, json=payload, headers=headers, timeout=20)
            if res.status_code == 200:
                res_data = res.json()
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                last_err = "[" + model_fullname + "] Code " + str(res.status_code) + ": " + res.text
        except Exception as e:
            last_err = str(e)
            continue

    raise RuntimeError("모든 Gemini 모델 호출 실패. (상세 에러: " + last_err + ")")

# ---------------------------------------------------------
# 3. API 키가 없어도 작동하는 스마트 자동 요약 추출기 (파이썬 기본 로직)
# ---------------------------------------------------------
def smart_fallback_summary(text, engine_name, lang_name):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 키워드 기반 추출 시도
    dates = []
    locations = []
    topics = []
    
    for line in lines:
        lower_line = line.lower()
        if any(k in lower_line for k in ['date', '날짜', '일시', 'period', '기간', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', '2026']):
            dates.append(line)
        elif any(k in lower_line for k in ['location', '장소', 'room', 'building', '호', '관', 'hall']):
            locations.append(line)
        elif any(k in lower_line for k in ['chapter', 'scope', 'topic', '범위', '단원', '과제', 'assignment']):
            topics.append(line)

    summary_md = "- **⚙️ 사용 엔진**: `" + engine_name + "`\n"
    summary_md += "- **🌐 목표 언어**: `" + lang_name + "`\n"
    
    if dates:
        summary_md += "- **📅 주요 일정/기한**: " + " / ".join(dates[:2]) + "\n"
    if locations:
        summary_md += "- **📍 장소 정보**: " + " / ".join(locations[:2]) + "\n"
    if topics:
        summary_md += "- **📚 주요 범위/내용**: " + " / ".join(topics[:2]) + "\n"
        
    # 만약 특별히 잡힌 게 없다면 첫 줄들을 핵심 요약으로 대체
    if not dates and not locations and not topics and lines:
        summary_md += "- **📝 핵심 요약**: " + lines[0] + "\n"
        
    return summary_md

# ---------------------------------------------------------
# 다국어 텍스트 사전
# ---------------------------------------------------------
TEXTS = {
    "한국어 (Korean)": {
        "title": "🌐 통합 학사 번역기 서비스",
        "subtitle": "환영합니다! 시작하기 전 서비스 설명과 API 가이드라인을 확인해 주세요.",
        "lang_label": "번역 결과로 출력될 언어를 선택하세요:",
        "guide_title": "📋 서비스 이용 가이드라인 및 상세 설명",
        "guide_content": (
            "### 📌 1. 앱 상세 설명\n"
            "- **다중 엔진 통합**: 기본 기계번역, **Google Gemini AI 번역**, **DeepL 번역(압도적 자연스러움)**을 입맛에 맞게 골라 쓸 수 있습니다.\n"
            "- **텍스트 비교 모드**: 일반 기계번역 결과와 Gemini AI의 전공/학술 특화 번역을 한 화면에서 나란히 비교할 수 있습니다.\n"
            "- **이미지 OCR 번역**: 원서, 전공 교재, 과제 캡처 이미지 등을 업로드하면 텍스트를 추출하고 자연스럽게 번역해 줍니다.\n\n"
            "### 🔑 2. API 키 발급 및 설정 가이드\n"
            "- **기본 자동 기계번역**: API 키 없이도 즉시 사용 가능합니다.\n"
            "- **Google Gemini API**: 학술 교재 이미지 분석 및 AI 요약 리포트를 위해 필요합니다.\n"
            "  - 🔗 [Google AI Studio 바로가기 (API 키 발급 링크)](https://aistudio.google.com/) 에서 무료로 발급받을 수 있습니다.\n"
            "- **DeepL API**: 압도적 자연스러움의 번역을 위해 필요합니다.\n"
            "  - 🔗 [DeepL API 무료/유료 계정 발급 링크](https://www.deepl.com/pro-api) 에서 발급받을 수 있습니다.\n"
            "- **사용 방법**: 첫 화면 진입 후 사이드바에서 사용할 엔진을 고르고 API 키를 입력하면 바로 활성화됩니다."
        ),
        "start_btn": "🚀 설정 확인 및 번역기 시작하기",
        "sidebar_title": "⚙️ 엔진 설정 및 안내",
        "engine_select": "번역 엔진 선택",
        "api_input": "API Key 입력 (Gemini/DeepL 전용)",
        "current_lang": "현재 설정된 목표 언어:",
        "back_btn": "🔄 첫 화면으로 돌아가기",
        "tab1": "📝 텍스트 번역 및 비교",
        "tab2": "🖼️ 이미지 번역 (Gemini)",
        "text_header": "텍스트 번역",
        "text_prompt": "번역할 텍스트를 입력하세요:",
        "text_btn": "번역 실행",
        "compare_mode": "⚖️ [비교 모드] 기본 기계번역 vs Gemini AI 번역 동시 실행",
        "img_header": "🖼️ 이미지 OCR 분석 및 번역",
        "img_prompt": "번역할 이미지 파일(원서/전공교재/캡처)을 업로드하세요 (PNG, JPG, JPEG)",
        "img_btn": "📷 이미지 분석 및 번역 실행",
        "warning_text": "⚠️ 번역할 텍스트를 입력해 주세요.",
        "spinner_text": "번역 진행 중입니다...",
        "spinner_img": "이미지에서 텍스트를 추출하고 번역하는 중입니다...",
        "success_res": "✨ 번역 결과:",
        "success_img": "✨ 이미지 분석 및 번역 결과:",
        "error_msg": "❌ 번역 중 에러가 발생했습니다: ",
        "summary_section": "⚡ AI 요약 리포트"
    },
    "영어 (English)": {
        "title": "🌐 Multi-Engine Academic Translator",
        "subtitle": "Welcome! Please review the service description and API guidelines before starting.",
        "lang_label": "Select the target output language for translation:",
        "guide_title": "📋 Service Guidelines & Detailed Description",
        "guide_content": (
            "### 📌 1. App Description\n"
            "- **Multi-Engine Integration**: Switch between Free Machine Translation, **Google Gemini AI**, and **DeepL (Ultra-natural)**.\n"
            "- **Comparison Mode**: Compare standard machine translation and Gemini AI translation side-by-side.\n"
            "- **Image OCR Translation**: Upload screenshots, textbook pages, or papers for text extraction and translation.\n\n"
            "### 🔑 2. API Key Setup Guide\n"
            "- **Free Machine Translation**: Available instantly without an API key.\n"
            "- **Google Gemini API**: Required for image OCR and AI summary reports.\n"
            "  - 🔗 Get your free key at [Google AI Studio Link](https://aistudio.google.com/).\n"
            "- **DeepL API**: Required for ultra-natural translations.\n"
            "  - 🔗 Get your DeepL API key at [DeepL API Link](https://www.deepl.com/pro-api)."
        ),
        "start_btn": "🚀 Confirm Settings & Start Translator",
        "sidebar_title": "⚙️ Engine Settings & Info",
        "engine_select": "Select Translation Engine",
        "api_input": "API Key (For Gemini/DeepL)",
        "current_lang": "Current Target Language:",
        "back_btn": "🔄 Return to Home",
        "tab1": "📝 Text Translation & Compare",
        "tab2": "🖼️ 이미지 번역 (Gemini)",
        "text_header": "Text Translation",
        "text_prompt": "Enter text to translate:",
        "text_btn": "Run Translation",
        "compare_mode": "⚖️ [Compare Mode] Run Free Machine vs Gemini AI Simultaneously",
        "img_header": "🖼️ Image OCR Analysis & Translation",
        "img_prompt": "Upload image file (PNG, JPG, JPEG)",
        "img_btn": "📷 Run Image Analysis & Translation",
        "warning_text": "⚠️ Please enter text to translate.",
        "spinner_text": "Translating...",
        "spinner_img": "Extracting text and translating image...",
        "success_res": "✨ Translation Result:",
        "success_img": "✨ Image Translation Result:",
        "error_msg": "❌ An error occurred: ",
        "summary_section": "⚡ AI Summary Report"
    }
}

lang_choice = st.session_state.get("target_lang", "한국어 (Korean)")
t = TEXTS.get(lang_choice, TEXTS["한국어 (Korean)"])

# ---------------------------------------------------------
# [1단계] 메인 첫 화면 (안내 및 설정)
# ---------------------------------------------------------
if not st.session_state.started:
    st.title("🌐 스마트 학사 번역기")
    st.subheader("환영합니다! 언어 설정과 API 가이드라인을 확인해 주세요.")
    
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
    st.markdown("### " + t_current['guide_title'])
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
    
    engine_options = [
        "기본 자동 기계번역 (키 불필요, 빠른 속도)", 
        "Google Gemini (문맥 및 전공 이해도 높음)", 
        "DeepL (압도적 자연스러움)"
    ]
    engine_choice = st.sidebar.selectbox(t['engine_select'], engine_options)
    api_key = st.sidebar.text_input(t['api_input'], type="password")
    
    st.sidebar.markdown("**현재 엔진:** `" + engine_choice + "`")
    st.sidebar.markdown("**" + t['current_lang'] + "**\n`" + st.session_state.target_lang + "`")
    
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

    # --- [탭 1: 텍스트 번역 및 비교] ---
    with tab1:
        st.header(t['text_header'])
        user_text = st.text_area(t['text_prompt'], height=180)
        
        is_compare = st.checkbox(t['compare_mode'], value=False)
        
        if st.button(t['text_btn'], use_container_width=True):
            if not user_text.strip():
                st.warning(t['warning_text'])
            else:
                final_translated_text = ""
                has_success = False

                if is_compare:
                    if not api_key:
                        st.warning("⚠️ 비교 모드에서 Gemini AI 번역 결과를 함께 보려면 사이드바에 **Gemini API 키**를 입력해 주세요.")
                    else:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🤖 기본 기계번역 결과")
                            with st.spinner("기계번역 실행 중..."):
                                try:
                                    free_res = free_google_translate(user_text, target_code)
                                    st.info(free_res)
                                    final_translated_text = free_res
                                except Exception as e:
                                    st.error("기계번역 오류: " + str(e))
                                    
                        with col2:
                            st.subheader("✨ Gemini AI 번역 결과")
                            with st.spinner("Gemini AI 번역 실행 중..."):
                                try:
                                    prompt = "다음 텍스트를 " + lang_name + "로 번역해줘. 어색한 직역투를 지우고 학술/전공 서적 스타일로 매끄럽게 번역 결과만 출력해줘:\n\n" + user_text
                                    ai_res = generate_gemini_auto(api_key, prompt)
                                    st.success(ai_res)
                                    final_translated_text = ai_res
                                    has_success = True
                                except Exception as e:
                                    st.error("Gemini AI 오류: " + str(e))

                else:
                    try:
                        if "DeepL" in engine_choice and api_key:
                            translator = deepl.Translator(api_key)
                            deepl_codes = {"한국어 (Korean)": "KO", "영어 (English)": "EN-US", "스페인어 (Spanish)": "ES", "러시아어 (Russian)": "RU", "일본어 (Japanese)": "JA"}
                            with st.spinner(t['spinner_text']):
                                result = translator.translate_text(user_text, target_lang=deepl_codes.get(lang_name, "EN-US"))
                            st.success(t['success_res'])
                            st.write(result.text)
                            final_translated_text = result.text
                            has_success = True
                        
                        elif "Google Gemini" in engine_choice and api_key:
                            prompt = "다음 텍스트를 " + lang_name + "로 번역해줘. 어색한 직역투를 지우고 매끄러운 자연스러운 표현으로 번역 결과만 출력해줘:\n\n" + user_text
                            with st.spinner(t['spinner_text']):
                                translated_res = generate_gemini_auto(api_key, prompt)
                            st.success(t['success_res'])
                            st.write(translated_res)
                            final_translated_text = translated_res
                            has_success = True
                            
                        else:
                            with st.spinner(t['spinner_text']):
                                translated_text = free_google_translate(user_text, target_code)

                            st.success(t['success_res'])
                            st.write(translated_text)
                            final_translated_text = translated_text
                            has_success = True
                            
                    except Exception as e:
                        st.error(t['error_msg'] + str(e))

                # ⚡ 어떤 엔진을 쓰든, API 키 유무와 무관하게 무조건 AI 요약 리포트 자동 생성
                if has_success and final_translated_text:
                    st.markdown("---")
                    st.subheader(t['summary_section'])
                    
                    summary_output = ""
                    if api_key:
                        try:
                            summary_prompt = "다음 번역된 텍스트
