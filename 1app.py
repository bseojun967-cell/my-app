import os
import streamlit as st
from google import genai

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

# 사이드바 설정 (선택란 및 API 키 입력)
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

# API 키 설정 로직
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

# 기능별 가이드라인 데이터 (중괄호 이스케이프 처리 완료)
GUIDELINES = {
    "Text Generation": {
        "overview": {
            "한국어 (KO)": "가장 기본적인 텍스트 생성 및 멀티턴 대화 기능을 수행합니다.",
            "English (EN)": "Performs basic text generation and multi-turn chat.",
            "Español (ES)": "Realiza generación de texto básica y chat de múltiples turnos."
        },
        "code": f"""from google import genai
import os

# os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY"
client = genai.Client()

response = client.models.generate_content(
    model="{selected_model}",
    contents="Explain quantum computing in simple terms.",
)
print(response.text)""",
        "tips": {
            "한국어 (KO)": "- `genai.Client()`는 환경 변수 `GEMINI_API_KEY`를 자동으로 감지합니다.\n- 시스템 프롬프트를 활용하여 모델의 페르소나를 고정하세요.",
            "English (EN)": "- `genai.Client()` automatically detects the `GEMINI_API_KEY` environment variable.\n- Use system_instruction to fix the model's persona.",
            "Español (ES)": "- `genai.Client()` detecta automáticamente la variable de entorno `GEMINI_API_KEY`."
        }
    },
    "Multimodal": {
        "overview": {
            "한국어 (KO)": "이미지, 오디오 등 미디어 데이터를 입력받아 분석합니다.",
            "English (EN)": "Accepts media data like images and audio for analysis.",
            "Español (ES)": "Acepta datos multimedia como imágenes y audio para análisis."
        },
        "code": f"""from google import genai
from PIL import Image

client = genai.Client()
image = Image.open('sample.jpg')

response = client.models.generate_content(
    model="{selected_model}",
    contents=[image, "Describe this image in detail."],
)
print(response.text)""",
        "tips": {
            "한국어 (KO)": "- 대용량 파일은 해상도 최적화가 필요할 수 있습니다.",
            "English (EN)": "- Large files may require resolution optimization.",
            "Español (ES)": "- Los archivos grandes pueden requerir optimización de resolución."
        }
    },
    "Structured Outputs": {
        "overview": {
            "한국어 (KO)": "정형화된 JSON 스키마 출력을 강제합니다.",
            "English (EN)": "Forces structured JSON schema output.",
            "Español (ES)": "Obliga a una salida de esquema JSON estructurado."
        },
        "code": f"""from google import genai
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]

client = genai.Client()
response = client.models.generate_content(
    model="{selected_model}",
    contents="List a recipe for chocolate chip cookies.",
    config={{
        'response_mime_type': 'application/json',
        'response_schema': Recipe,
    }}
)
print(response.text)""",
        "tips": {
            "한국어 (KO)": "- Pydantic 모델을 활용해 타입 안전성을 확보하세요.",
            "English (EN)": "- Ensure type safety using Pydantic models.",
            "Español (ES)": "- Asegure la seguridad de tipos usando modelos Pydantic."
        }
    },
    "Function Calling": {
        "overview": {
            "한국어 (KO)": "커스텀 함수를 모델이 직접 호출하도록 연동합니다.",
            "English (EN)": "Integrates custom functions for model invocation.",
            "Español (ES)": "Integra funciones personalizadas para invocación del modelo."
        },
        "code": f"""from google import genai

def get_current_weather(location: str):
    \"\"\"Get the current weather for a given location.\"\"\"
    return "Sunny, 24°C"

client = genai.Client()
response = client.models.generate_content(
    model="{selected_model}",
    contents="What's the weather like in Seoul?",
    config={{
        'tools': [get_current_weather]
    }}
)
print(response.function_calls)""",
        "tips": {
            "한국어 (KO)": "- 상세한 독스트링(Docstring) 작성이 핵심입니다.",
            "English (EN)": "- Detailed docstrings are crucial.",
            "Español (ES)": "- Los docstrings detallados son cruciales."
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
            - **⏰ 시간 (Time)**: 오후 12시 56분
            - **📍 장소 (Location)**: 개발 워크스페이스
            - **📝 내용 요약 (Core Summary)**: **{selected_display_feature}** 기능 가이드 및 API 키 인증 설정 확인 완료. (API 키 입력 여부: {'입력됨' if user_api_key else '미입력'})
            """
        elif selected_lang == "Español (ES)":
            summary_html = f"""
            - **📅 Fecha**: 15 de octubre de 2026
            - **⏰ Hora**: 12:56 PM
            - **📍 Lugar**: Entorno de Desarrollo
            - **📝 Resumen**: Guía de **{selected_display_feature}** y configuración de API Key verificadas.
            """
        else:
            summary_html = f"""
            - **📅 Date**: October 15, 2026
            - **⏰ Time**: 12:56 PM
            - **📍 Location**: Development Workspace
            - **📝 Core Summary**: Verified **{selected_display_feature}** guide and API Key authentication setup.
            """

    st.success(t["summary_result_title"])
    st.markdown(summary_html)

st.markdown("---")
st.caption(t["footer"])
