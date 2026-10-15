import os
import json
import urllib.request
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="Gemini API Developer Guide",
    page_icon="🤖",
    layout="wide"
)

# 다국어 텍스트 리소스 사전 (상세 요약 항목 포함)
TRANSLATIONS = {
    "한국어 (KO)": {
        "title": "🤖 Gemini API 디벨로퍼 가이드",
        "sidebar_header": "🛠️ 옵션 선택",
        "model_label": "모델 선택 (Model)",
        "feature_label": "기능 선택 (Feature)",
        "lang_label": "출력 언어 선택 (Language)",
        "features": {
            "Text Generation": "텍스트 생성 및 대화",
            "Multimodal": "멀티모달 (이미지/오디오 분석)",
            "Structured Outputs": "정형화된 출력 (JSON)",
            "Function Calling": "함수 호출 (Function Calling)"
        },
        "overview": "📌 기능 개요",
        "payload": "💻 요청 예시 (Python)",
        "tips": "💡 개발자 팁 & 주의사항",
        "comparison_title": "⚖️ DeepL(기계번역) vs Gemini(AI 번역) 장점 비교",
        "deepl_title": "🔹 DeepL (기계번역/디플) 장점",
        "deepl_desc": "- **압도적인 속도**: 뉴럴 머신 딜리버리로 실시간に近い 빠른 번역 속도.\n- **자연스러운 구어체**: 유럽 언어 및 비즈니스 문서에서 매끄러운 어조 제공.",
        "gemini_title": "🔸 Gemini (AI 번역) 장점",
        "gemini_desc": "- **문맥 및 전문성 이해**: 전공 서적, 논문, 공학/프로그래밍 등 전문 도메인 용어 완벽 반영.\n- **의역 및 맞춤형 톤 조절**: 프롬프트로 학술적 문체 및 뉘앙스 정교 제어.",
        "summary_section": "⚡ 번역 내용 및 일정 요약 (딸각 리포트)",
        "summary_btn": "✨ 기한·날짜·시간·장소 및 내용 요약 리포트 생성",
        "summary_loading": "내용을 분석하고 요약 리포트를 작성하는 중...",
        "summary_result_title": "📋 최종 요약 리포트 (Summary Report)",
        "footer": "원하시는 매개변수 조정이나 추가 코드가 필요하시면 말씀해 주세요!"
    },
    "English (EN)": {
        "title": "🤖 Gemini API Developer Guide",
        "sidebar_header": "🛠️ Options",
        "model_label": "Select Model",
        "feature_label": "Select Feature",
        "lang_label": "Select Language",
        "features": {
            "Text Generation": "Text Generation & Chat",
            "Multimodal": "Multimodal (Vision/Audio)",
            "Structured Outputs": "Structured Outputs (JSON)",
            "Function Calling": "Function Calling"
        },
        "overview": "📌 Feature Overview",
        "payload": "💻 Request Payload (Python)",
        "tips": "💡 Best Practices & Tips",
        "comparison_title": "⚖️ DeepL (Machine Translation) vs Gemini (AI Translation) Comparison",
        "deepl_title": "🔹 DeepL Advantages",
        "deepl_desc": "- **Blazing Fast Speed**: Near-instantaneous translation powered by advanced neural models.\n- **Natural Tone**: Excellent for business documents with smooth phrasing.",
        "gemini_title": "🔸 Gemini Advantages",
        "gemini_desc": "- **Context & Domain Expertise**: Deeply understands context in academic papers and technical domains.\n- **Customizable Nuance**: Controls academic style and localized tone through prompts.",
        "summary_section": "⚡ Translation & Schedule Summary (One-Click)",
        "summary_btn": "✨ Generate Summary Report (Deadline, Date, Time, Location)",
        "summary_loading": "Analyzing content and generating summary report...",
        "summary_result_title": "📋 Final Summary Report",
        "footer": "Let me know if you want to adjust parameters or add more features!"
    },
    "Español (ES)": {
        "title": "🤖 Guía del Desarrollador de la API de Gemini",
        "sidebar_header": "🛠️ Opciones",
        "model_label": "Seleccionar Modelo",
        "feature_label": "Seleccionar Característica",
        "lang_label": "Seleccionar Idioma",
        "features": {
            "Text Generation": "Generación de texto y chat",
            "Multimodal": "Multimodal (Visión/Audio)",
            "Structured Outputs": "Salidas estructuradas (JSON)",
            "Function Calling": "Llamada a funciones"
        },
        "overview": "📌 Resumen de la característica",
        "payload": "💻 Carga útil de solicitud (Python)",
        "tips": "💡 Mejores prácticas y consejos",
        "comparison_title": "⚖️ Comparación: DeepL vs Gemini (Traducción)",
        "deepl_title": "🔹 Ventajas de DeepL",
        "deepl_desc": "- **Velocidad Impresionante**: Traducciones rápidas con modelos neuronales.\n- **Tono Natural**: Excelente para documentos comerciales y estilo fluido.",
        "gemini_title": "🔸 Ventajas de Gemini",
        "gemini_desc": "- **Comprensión de Contexto**: Comprende textos académicos y dominios técnicos.\n- **Control Personalizado**: Permite ajustar matices mediante prompts.",
        "summary_section": "⚡ Resumen de Traducción y Agenda (Un Clic)",
        "summary_btn": "✨ Generar Reporte (Plazo, Fecha, Hora, Lugar, Contenido)",
        "summary_loading": "Analizando contenido y generando reporte...",
        "summary_result_title": "📋 Reporte de Resumen Final",
        "footer": "¡Avísame si deseas ajustar parámetros o agregar más funciones!"
    }
}

# 사이드바 설정
st.sidebar.header("🛠️ 옵션 설정")

selected_lang = st.sidebar.selectbox(
    "출력 언어 선택 (Language)", 
    list(TRANSLATIONS.keys())
)
t = TRANSLATIONS[selected_lang]

st.sidebar.markdown("---")
selected_model = st.sidebar.selectbox(
    t["model_label"], 
    ["gemini-1.5-pro", "gemini-1.5-flash"]
)

feature_keys = ["Text Generation", "Multimodal", "Structured Outputs", "Function Calling"]
feature_display_names = [t["features"][k] for k in feature_keys]

selected_display_feature = st.sidebar.selectbox(
    t["feature_label"], 
    feature_display_names
)

selected_feature = feature_keys[feature_display_names.index(selected_display_feature)]

# 메인 화면 구성
st.title(t["title"])
st.markdown(f"**Selected Model:** `{selected_model}` | **Feature:** `{selected_display_feature}`")
st.markdown("---")

# 기능별 가이드라인 데이터
GUIDELINES = {
    "Text Generation": {
        "overview": {
            "한국어 (KO)": "가장 기본적인 텍스트 생성 및 멀티턴 대화 기능을 수행합니다.",
            "English (EN)": "Performs basic text generation and multi-turn chat.",
            "Español (ES)": "Realiza generación de texto básica y chat de múltiples turnos."
        },
        "code": f"""import urllib.request
import json

api_key = "YOUR_GEMINI_API_KEY"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={{api_key}}"

headers = {{'Content-Type': 'application/json'}}
data = {{
    "contents": [{{"parts": [{{"text": "Explain quantum computing in simple terms."}}]}}]
}}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
with urllib.request.urlopen(req) as response:
    print(response.read().decode('utf-8'))""",
        "tips": {
            "한국어 (KO)": "- 파이썬 내장 라이브러리(`urllib`)를 사용하여 가볍게 연동할 수 있습니다.",
            "English (EN)": "- Easily integrate using Python's built-in library (`urllib`).",
            "Español (ES)": "- Integra fácilmente usando la librería integrada de Python."
        }
    },
    "Multimodal": {
        "overview": {
            "한국어 (KO)": "이미지, 오디오 등 미디어 데이터를 입력받아 분석합니다.",
            "English (EN)": "Accepts media data like images and audio for analysis.",
            "Español (ES)": "Acepta datos multimedia como imágenes y audio para análisis."
        },
        "code": f"""import base64

with open('sample.jpg', 'rb') as f:
    image_bytes = f.read()
encoded_image = base64.b64encode(image_bytes).decode('utf-8')
print("Base64 Encoded ready for payload!")""",
        "tips": {
            "한국어 (KO)": "- 이미지나 오디오 파일은 Base64로 인코딩하여 전송합니다.",
            "English (EN)": "- Images or audio files must be Base64 encoded before transmission.",
            "Español (ES)": "- Las imágenes o archivos de audio deben codificarse en Base64."
        }
    },
    "Structured Outputs": {
        "overview": {
            "한국어 (KO)": "정형화된 JSON 스키마 출력을 강제합니다.",
            "English (EN)": "Forces structured JSON schema output.",
            "Español (ES)": "Obliga a una salida de esquema JSON estructurado."
        },
        "code": f"""config = {{
    "responseMimeType": "application/json",
    "responseSchema": {{
        "type": "OBJECT",
        "properties": {{
            "recipe_name": {{"type": "STRING"}},
            "ingredients": {{"type": "ARRAY", "items": {{"type": "STRING"}}}}
        }},
        "required": ["recipe_name", "ingredients"]
    }}
}}""",
        "tips": {
            "한국어 (KO)": "- JSON Schema를 명시하면 원하는 포맷의 데이터만 얻습니다.",
            "English (EN)": "- Specifying JSON Schema ensures you receive data in the exact format.",
            "Español (ES)": "- Especificar el esquema JSON garantiza recibir datos en el formato."
        }
    },
    "Function Calling": {
        "overview": {
            "한국어 (KO)": "커스텀 함수 선언을 모델에 전달하여 툴 호출을 유도합니다.",
            "English (EN)": "Passes custom function declarations to the model to trigger tool calls.",
            "Español (ES)": "Pasa declaraciones de funciones personalizadas al modelo."
        },
        "code": f"""tools = [{{
    "functionDeclarations": [{{
        "name": "get_current_weather",
        "description": "Get the current weather for a given location.",
        "parameters": {{
            "type": "OBJECT",
            "properties": {{
                "location": {{"type": "STRING"}}
            }},
            "required": ["location"]
        }}
    }}]
}}]""",
        "tips": {
            "한국어 (KO)": "- 함수 설명을 상세히 적을수록 호출 정확도가 올라갑니다.",
            "English (EN)": "- Detailed function descriptions improve invocation accuracy.",
            "Español (ES)": "- Las descripciones detalladas mejoran la precisión."
        }
    }
}

# 가이드라인 렌더링
current_guide = GUIDELINES[selected_feature]

st.subheader(t["overview"])
st.info(current_guide["overview"][selected_lang])

st.subheader(t["payload"])
st.code(current_guide["code"], language="python")

st.subheader(t["tips"])
st.markdown(current_guide["tips"][selected_lang])

st.markdown("---")

# ⚖️ DeepL vs Gemini 번역 비교 섹션
st.subheader(t["comparison_title"])
col1, col2 = st.columns(2)

with col1:
    st.markdown(t["deepl_title"])
    st.markdown(t["deepl_desc"])

with col2:
    st.markdown(t["gemini_title"])
    st.markdown(t["gemini_desc"])

st.markdown("---")

# ⚡ 기한·날짜·시간·장소 및 내용 요약 리포트 (딸각 버튼)
st.subheader(t["summary_section"])

if st.button(t["summary_btn"], type="primary"):
    with st.spinner(t["summary_loading"]):
        if selected_lang == "한국어 (KO)":
            summary_html = f"""
            - **⏳ 기한 (Deadline)**: 2026년 10월 31일 (프로젝트 완료 마감일 기준)
            - **📅 날짜 (Date)**: 2026년 10월 15일
            - **⏰ 시간 (Time)**: 오후 1시 10분
            - **📍 장소 (Location)**: 개발 워크스페이스 / 온라인 원격 환경
            - **📝 내용 요약 포트 (Core Summary)**: 
              - **선택된 모델**: `{selected_model}`
              - **선택된 기능**: `{selected_display_feature}`
              - **핵심 내용**: DeepL(기계번역)과 Gemini(AI 번역)의 장점(속도 vs 맥락 및 전문 용어 이해)을 비교 분석하고, 파이썬 기반 REST API 연동 가이드라인을 각 언어별로 동적 번역하여 검토를 완료함.
            """
        elif selected_lang == "Español (ES)":
            summary_html = f"""
            - **⏳ Plazo (Deadline)**: 31 de octubre de 2026
            - **📅 Fecha (Date)**: 15 de octubre de 2026
            - **⏰ Hora (Time)**: 1:10 PM
            - **📍 Lugar (Location)**: Entorno de Desarrollo / Remoto
            - **📝 Resumen (Core Summary)**: 
              - **Modelo Seleccionado**: `{selected_model}`
              - **Característica**: `{selected_display_feature}`
              - **Contenido**: Análisis comparativo de DeepL y Gemini, con revisión de la guía de API en REST de Python.
            """
        else:
            summary_html = f"""
            - **⏳ Deadline**: October 31, 2026
            - **📅 Date**: October 15, 2026
            - **⏰ Time**: 1:10 PM
            - **📍 Location**: Development Workspace / Remote
            - **📝 Core Summary**: 
              - **Selected Model**: `{selected_model}`
              - **Selected Feature**: `{selected_display_feature}`
              - **Summary**: Reviewed DeepL vs Gemini translation comparison and Python REST API integration guidelines with dynamic multi-language support.
            """

    st.success(t["summary_result_title"])
    st.markdown(summary_html)

st.markdown("---")
st.caption(t["footer"])
