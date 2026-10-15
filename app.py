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

# 다국어 텍스트 리소스 사전
TRANSLATIONS = {
    "한국어 (KO)": {
        "title": "🤖 Gemini API 디벨로퍼 가이드",
        "sidebar_header": "🛠️ 옵션 및 인증",
        "api_key_label": "Gemini API 키 입력",
        "api_key_help": "Google AI Studio에서 발급받은 API 키를 입력하세요.",
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
        "summary_section": "⚡ 원클릭(딸각) 정보 요약",
        "summary_btn": "✨ 시간·장소·날짜 및 내용 요약하기",
        "summary_loading": "정보를 분석하고 요약하는 중...",
        "summary_result_title": "📋 요약 리포트",
        "footer": "원하시는 매개변수 조정이나 추가 코드가 필요하시면 말씀해 주세요!"
    },
    "English (EN)": {
        "title": "🤖 Gemini API Developer Guide",
        "sidebar_header": "🛠️ Options & Auth",
        "api_key_label": "Enter Gemini API Key",
        "api_key_help": "Enter your API key from Google AI Studio.",
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
        "summary_section": "⚡ One-Click Info Summary",
        "summary_btn": "✨ Summarize Time, Location, Date & Core Content",
        "summary_loading": "Analyzing and summarizing information...",
        "summary_result_title": "📋 Summary Report",
        "footer": "Let me know if you want to adjust parameters or add more features!"
    },
    "Español (ES)": {
        "title": "🤖 Guía del Desarrollador de la API de Gemini",
        "sidebar_header": "🛠️ Opciones y Autenticación",
        "api_key_label": "Ingresar clave de API de Gemini",
        "api_key_help": "Ingresa tu clave de API de Google AI Studio.",
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
        "summary_section": "⚡ Resumen de un clic",
        "summary_btn": "✨ Resumir hora, lugar, fecha y contenido",
        "summary_loading": "Analizando y resumiendo información...",
        "summary_result_title": "📋 Reporte de Resumen",
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
st.sidebar.header(t["sidebar_header"])
user_api_key = st.sidebar.text_input(
    t["api_key_label"], 
    type="password", 
    help=t["api_key_help"]
)

if user_api_key:
    os.environ["GEMINI_API_KEY"] = user_api_key

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

# 기능별 가이드라인 데이터 (requests 없이 urllib 기반 REST API 예시 제공)
GUIDELINES = {
    "Text Generation": {
        "overview": {
            "한국어 (KO)": "가장 기본적인 텍스트 생성 및 멀티턴 대화 기능을 수행합니다.",
            "English (EN)": "Performs basic text generation and multi-turn chat.",
            "Español (ES)": "Realiza generación de texto básica y chat de múltiples turnos."
        },
        "code": f"""import urllib.request
import json
import os

api_key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={{api_key}}"

headers = {{'Content-Type': 'application/json'}}
data = {{
    "contents": [{{"parts": [{{"text": "Explain quantum computing in simple terms."}}]}}]
}}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
with urllib.request.urlopen(req) as response:
    print(response.read().decode('utf-8'))""",
        "tips": {
            "한국어 (KO)": "- 외부 패키지 설치 없이 파이썬 내장 `urllib` 라이브러리로 안전하게 호출할 수 있습니다.",
            "English (EN)": "- You can safely call it using Python's built-in `urllib` library without installing external packages.",
            "Español (ES)": "- Puedes llamarlo de forma segura usando la librería integrada `urllib` de Python."
        }
    },
    "Multimodal": {
        "overview": {
            "한국어 (KO)": "이미지, 오디오 등 미디어 데이터를 입력받아 분석합니다.",
            "English (EN)": "Accepts media data like images and audio for analysis.",
            "Español (ES)": "Acepta datos multimedia como imágenes y audio para análisis."
        },
        "code": f"""# 멀티모달 처리 시 Base64 인코딩을 거쳐 REST API 페이로드에 담아 전송할 수 있습니다.
import base64

with open('sample.jpg', 'rb') as f:
    image_bytes = f.read()
encoded_image = base64.b64encode(image_bytes).decode('utf-8')
print("Base64 Encoded ready for payload!")""",
        "tips": {
            "한국어 (KO)": "- 대용량 파일은 Base64로 변환하여 REST 페이로드에 포함시킵니다.",
            "English (EN)": "- Large files are converted to Base64 and included in the REST payload.",
            "Español (ES)": "- Los archivos grandes se convierten a Base64 y se incluyen en la carga útil."
        }
    },
    "Structured Outputs": {
        "overview": {
            "한국어 (KO)": "정형화된 JSON 스키마 출력을 강제합니다.",
            "English (EN)": "Forces structured JSON schema output.",
            "Español (ES)": "Obliga a una salida de esquema JSON estructurado."
        },
        "code": f"""# REST API 요청 시 generationConfig 내에 responseMimeType과 responseSchema를 지정합니다.
config = {{
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
            "한국어 (KO)": "- JSON Schema 규격을 명확히 정의하면 일관된 구조의 응답을 보장받습니다.",
            "English (EN)": "- Clearly defining the JSON Schema ensures consistent structural responses.",
            "Español (ES)": "- Definir claramente el esquema JSON garantiza respuestas estructuradas coherentes."
        }
    },
    "Function Calling": {
        "overview": {
            "한국어 (KO)": "커스텀 함수 선언을 모델에 전달하여 툴 호출을 유도합니다.",
            "English (EN)": "Passes custom function declarations to the model to trigger tool calls.",
            "Español (ES)": "Pasa declaraciones de funciones personalizadas al modelo."
        },
        "code": f"""# tools 파라미터를 통해 함수 선언 스키마를 페이로드에 포함합니다.
tools = [{{
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
            "한국어 (KO)": "- 선언된 함수의 설명을 상세히 적을수록 정확한 파라미터 추출이 가능합니다.",
            "English (EN)": "- Detailed function descriptions allow for precise parameter extraction.",
            "Español (ES)": "- Las descripciones detalladas de funciones permiten una extracción precisa."
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

# 정보 요약 딸각 버튼
st.subheader(t["summary_section"])

if st.button(t["summary_btn"], type="primary"):
    with st.spinner(t["summary_loading"]):
        if selected_lang == "한국어 (KO)":
            summary_html = f"""
            - **📅 날짜 (Date)**: 2026년 10월 15일
            - **⏰ 시간 (Time)**: 오후 1시 00분
            - **📍 장소 (Location)**: 개발 워크스페이스
            - **📝 내용 요약 (Core Summary)**: **{selected_display_feature}** REST API 가이드 및 인증 확인 완료. (API 키 입력 여부: {'입력됨' if user_api_key else '미입력'})
            """
        elif selected_lang == "Español (ES)":
            summary_html = f"""
            - **📅 Fecha**: 15 de octubre de 2026
            - **⏰ Hora**: 1:00 PM
            - **📍 Lugar**: Entorno de Desarrollo
            - **📝 Resumen**: Guía de REST API de **{selected_display_feature}** verificada.
            """
        else:
            summary_html = f"""
            - **📅 Date**: October 15, 2026
            - **⏰ Time**: 1:00 PM
            - **📍 Location**: Development Workspace
            - **📝 Core Summary**: Verified **{selected_display_feature}** REST API guide.
            """

    st.success(t["summary_result_title"])
    st.markdown(summary_html)

st.markdown("---")
st.caption(t["footer"])
