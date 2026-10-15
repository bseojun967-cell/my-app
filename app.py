import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="학사 번역기 | Academic Translator", page_icon="🌐", layout="centered")

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
        "title": "🌐 학사 번역기 서비스",
        "subtitle": "환영합니다! 시작하기 전 기본 언어 설정과 가이드라인을 확인해 주세요.",
        "lang_label": "번역 결과로 출력될 언어를 선택하세요:",
        "guide_title": "📋 이용 및 안내 가이드라인",
        "guide_content": """
        🔑 **1. API 키 준비 안내**
        - 본 번역기는 **Google Gemini API**를 활용합니다.
        - 번역을 진행하려면 서비스 진입 후 왼쪽 사이드바에 본인의 **Gemini API Key**를 입력하셔야 합니다.
        - API 키가 없으신 경우 [Google AI Studio](https://aistudio.google.com/)에서 무료로 발급받으실 수 있습니다.

        📝 **2. 텍스트 번역 가이드**
        - 단문부터 장문(학술 논문, 에세이, 과제 등)까지 자연스럽게 번역을 지원합니다.
        - 전문 용어나 문맥 구별이 필요한 경우 원문의 맥락을 살려 최적의 번역을 제공합니다.

        🖼️ **3. 이미지 번역 가이드**
        - 캡처본, 문서 스캔본 등의 이미지 파일(PNG, JPG, JPEG)을 업로드할 수 있습니다.
        - 이미지 속 글자를 AI가 자동으로 인식하고 추출하여 선택한 언어로 즉시 번역해 드립니다.

        🔒 **4. 보안 및 데이터 보호**
        - 사용자가 입력한 API 키 및 텍스트/이미지 데이터는 **서버에 절대로 저장되지 않으며**, 번역 처리 직후 즉시 소멸합니다.
        """,
        "start_btn": "🚀 설정 확인 및 번역기 시작하기",
        "sidebar_title": "⚙️ 설정 및 안내",
        "api_input": "Gemini API Key 입력",
        "current_lang": "현재 설정된 목표 언어:",
        "back_btn": "🔄 첫 화면(언어/가이드)으로 돌아가기",
        "tab1": "📝 텍스트 번역",
        "tab2": "🖼️ 이미지 번역",
        "text_header": "텍스트 번역",
        "text_prompt": "번역할 텍스트를 입력하세요:",
        "text_btn": "텍스트 번역 실행",
        "img_header": "이미지 번역",
        "img_prompt": "이미지 파일을 업로드하세요 (PNG, JPG, JPEG)",
        "img_btn": "이미지 번역 실행",
        "warning_api": "⚠️ 사이드바에 Gemini API 키를 먼저 입력해 주세요.",
        "warning_text": "⚠️ 번역할 텍스트를 입력해 주세요.",
        "spinner_text": "번역 진행 중입니다...",
        "spinner_img": "이미지 분석 및 번역 진행 중입니다...",
        "success_res": "✨ 번역 결과:",
        "success_img": "✨ 이미지 번역 결과:",
        "error_msg": "❌ 번역 중 에러가 발생했습니다: "
    },
    "영어 (English)": {
        "title": "🌐 Academic Translator Service",
        "subtitle": "Welcome! Please review the language settings and guidelines before starting.",
        "lang_label": "Select the target output language for translation:",
        "guide_title": "📋 Guidelines & Instructions",
        "guide_content": """
        🔑 **1. API Key Notice**
        - This translator utilizes the **Google Gemini API**.
        - To proceed with translations, you must enter your **Gemini API Key** in the left sidebar.
        - If you don't have an API key, you can get one for free at [Google AI Studio](https://aistudio.google.com/).

        📝 **2. Text Translation Guide**
        - Supports natural translations from short sentences to long documents (academic papers, essays, assignments, etc.).
        - Provides optimal translations by preserving context for specialized terminology.

        🖼️ **3. Image Translation Guide**
        - Upload image files (PNG, JPG, JPEG) such as screenshots or scanned documents.
        - AI automatically recognizes and extracts text from images, instantly translating it into your chosen language.

        🔒 **4. Security & Data Protection**
        - Your entered API key and text/image data are **never saved on our servers** and are immediately discarded after processing.
        """,
        "start_btn": "🚀 Confirm Settings & Start Translator",
        "sidebar_title": "⚙️ Settings & Info",
        "api_input": "Enter Gemini API Key",
        "current_lang": "Current Target Language:",
        "back_btn": "🔄 Return to Home (Language/Guide)",
        "tab1": "📝 Text Translation",
        "tab2": "🖼️ Image Translation",
        "text_header": "Text Translation",
        "text_prompt": "Enter text to translate:",
        "text_btn": "Run Text Translation",
        "img_header": "Image Translation",
        "img_prompt": "Upload image file (PNG, JPG, JPEG)",
        "img_btn": "Run Image Translation",
        "warning_api": "⚠️ Please enter your Gemini API key in the sidebar first.",
        "warning_text": "⚠️ Please enter text to translate.",
        "spinner_text": "Translating...",
        "spinner_img": "Analyzing and translating image...",
        "success_res": "✨ Translation Result:",
        "success_img": "✨ Image Translation Result:",
        "error_msg": "❌ An error occurred during translation: "
    },
    "스페인어 (Spanish)": {
        "title": "🌐 Servicio de Traducción Académica",
        "subtitle": "¡Bienvenido! Revise la configuración de idioma y las pautas antes de comenzar.",
        "lang_label": "Seleccione el idioma de destino para la traducción:",
        "guide_title": "📋 Pautas e Instrucciones",
        "guide_content": """
        🔑 **1. Aviso sobre la Clave API**
        - Este traductor utiliza la **Google Gemini API**.
        - Para traducir, debe ingresar su **Clave API de Gemini** en la barra lateral izquierda.
        - Si no tiene una clave, puede obtener una gratis en [Google AI Studio](https://aistudio.google.com/).

        📝 **2. Guía de Traducción de Texto**
        - Admite traducciones naturales desde oraciones cortas hasta documentos largos (artículos académicos, ensayos, tareas).
        - Proporciona traducciones óptimas preservando el contexto y la terminología técnica.

        🖼️ **3. Guía de Traducción de Imágenes**
        - Puede subir archivos de imagen (PNG, JPG, JPEG) como capturas o documentos escaneados.
        - La IA reconoce y extrae texto de las imágenes, traduciéndolo al instante al idioma seleccionado.

        🔒 **4. Seguridad y Protección de Datos**
        - Su clave API y los datos de texto/imagen **nunca se guardan en nuestros servidores** y se eliminan de inmediato tras el procesamiento.
        """,
        "start_btn": "🚀 Confirmar configuración e iniciar",
        "sidebar_title": "⚙️ Configuración",
        "api_input": "Ingrese Clave API de Gemini",
        "current_lang": "Idioma de destino actual:",
        "back_btn": "🔄 Volver al inicio (Idioma/Guía)",
        "tab1": "📝 Traducción de Texto",
        "tab2": "🖼️ Traducción de Imágenes",
        "text_header": "Traducción de Texto",
        "text_prompt": "Ingrese el texto a traducir:",
        "text_btn": "Ejecutar traducción de texto",
        "img_header": "Traducción de Imágenes",
        "img_prompt": "Subir archivo de imagen (PNG, JPG, JPEG)",
        "img_btn": "Ejecutar traducción de imagen",
        "warning_api": "⚠️ Por favor, ingrese su clave API de Gemini en la barra lateral.",
        "warning_text": "⚠️ Por favor, ingrese el texto a traducir.",
        "spinner_text": "Traduciendo...",
        "spinner_img": "Analizando y traduciendo imagen...",
        "success_res": "✨ Resultado de la traducción:",
        "success_img": "✨ Resultado de traducción de imagen:",
        "error_msg": "❌ Ocurrió un error durante la traducción: "
    },
    "러시아어 (Russian)": {
        "title": "🌐 Академический Служба Перевода",
        "subtitle": "Добро пожаловать! Пожалуйста, ознакомьтесь с языковыми настройками и инструкциями.",
        "lang_label": "Выберите целевой язык для перевода:",
        "guide_title": "📋 Руководство и Инструкции",
        "guide_content": """
        🔑 **1. Информация об API-ключе**
        - Этот переводчик использует **Google Gemini API**.
        - Для перевода необходимо ввести ваш **API-ключ Gemini** на боковой панели слева.
        - Если у вас нет ключа, вы можете получить его бесплатно в [Google AI Studio](https://aistudio.google.com/).

        📝 **2. Руководство по переводу текста**
        - Поддерживает естественный перевод от коротких фраз до длинных документов (академические статьи, эссе).
        - Обеспечивает качественный перевод с учетом контекста и специальной терминологии.

        🖼️ **3. Руководство по переводу изображений**
        - Вы можете загружать изображения (PNG, JPG, JPEG) такие как скриншоты или сканы документов.
        - ИИ автоматически распознает текст на изображении и мгновенно переводит его на выбранный язык.

        🔒 **4. Безопасность и защита данных**
        - Введенный вами ключ API и данные **никогда не сохраняются на серверах** и удаляются сразу после обработки.
        """,
        "start_btn": "🚀 Подтвердить настройки и начать",
        "sidebar_title": "⚙️ Настройки",
        "api_input": "Введите API-ключ Gemini",
        "current_lang": "Текущий целевой язык:",
        "back_btn": "🔄 Вернуться на главную (Язык/Инструкция)",
        "tab1": "📝 Перевод текста",
        "tab2": "🖼️ Перевод изображений",
        "text_header": "Перевод текста",
        "text_prompt": "Введите текст для перевода:",
        "text_btn": "Выполнить перевод текста",
        "img_header": "Перевод изображений",
        "img_prompt": "Загрузите файл изображения (PNG, JPG, JPEG)",
        "img_btn": "Выполнить перевод изображения",
        "warning_api": "⚠️ Сначала введите API-ключ Gemini на боковой панели.",
        "warning_text": "⚠️ Пожалуйста, введите текст для перевода.",
        "spinner_text": "Перевод...",
        "spinner_img": "Анализ и перевод изображения...",
        "success_res": "✨ Результат перевода:",
        "success_img": "✨ Результат перевода изображения:",
        "error_msg": "❌ Произошла ошибка при переводе: "
    },
    "일본어 (Japanese)": {
        "title": "🌐 学術翻訳サービス",
        "subtitle": "ようこそ！開始する前に言語設定とガイドラインをご確認ください。",
        "lang_label": "翻訳の出力言語を選択してください：",
        "guide_title": "📋 ご利用ガイドライン",
        "guide_content": """
        🔑 **1. APIキーのご案内**
        - 本翻訳機は **Google Gemini API** を活用しています。
        - 翻訳を行うには、サイドバーにご自身の **Gemini API Key** を入力する必要があります。
        - キーをお持ちでない場合は、[Google AI Studio](https://aistudio.google.com/) から無料で取得できます。

        📝 **2. テキスト翻訳ガイド**
        - 短文から長文（学術論文、エッセイ、課題など）まで自然な翻訳をサポートします。
        - 専門用語や文脈を考慮した最適な翻訳を提供します。

        🖼️ **3. 画像翻訳ガイド**
        - スクリーンショットや文書スキャンなどの画像ファイル（PNG、JPG、JPEG）をアップロードできます。
        - AIが画像内の文字を自動認識・抽出し、選択した言語へ即座に翻訳します。

        🔒 **4. セキュリティとデータ保護**
        - 入力されたAPIキーおよびデータは**サーバーに一切保存されず**、処理完了後直ちに消去されます。
        """,
        "start_btn": "🚀 設定を確認して翻訳を開始",
        "sidebar_title": "⚙️ 設定と情報",
        "api_input": "Gemini API Keyを入力",
        "current_lang": "現在の目標言語：",
        "back_btn": "🔄 ホームに戻る（言語/ガイド）",
        "tab1": "📝 テキスト翻訳",
        "tab2": "🖼️ 画像翻訳",
        "text_header": "テキスト翻訳",
        "text_prompt": "翻訳するテキストを入力してください：",
        "text_btn": "テキスト翻訳を実行",
        "img_header": "画像翻訳",
        "img_prompt": "画像ファイルをアップロードしてください (PNG, JPG, JPEG)",
        "img_btn": "画像翻訳を実行",
        "warning_api": "⚠️ サイドバーにGemini APIキーを先に入力してください。",
        "warning_text": "⚠️ 翻訳するテキストを入力してください。",
        "spinner_text": "翻訳中...",
        "spinner_img": "画像解析および翻訳中...",
        "success_res": "✨ 翻訳結果：",
        "success_img": "✨ 画像翻訳結果：",
        "error_msg": "❌ 翻訳中にエラーが発生しました： "
    }
}

# 기본 선택 언어 텍스트 세트 로드 (등록되지 않은 언어는 영어 기본값 처리)
lang_choice = st.session_state.get("target_lang", "한국어 (Korean)")
t = TEXTS.get(lang_choice, TEXTS["한국어 (Korean)"])

# ---------------------------------------------------------
# [1단계] 메인 첫 화면: 언어 설정 & 가이드라인
# ---------------------------------------------------------
if not st.session_state.started:
    st.title("🌐 학사 번역기 서비스 / Academic Translator")
    st.subheader("환영합니다! 아래에서 사용할 언어와 가이드라인을 확인해 주세요.")
    
    st.divider()

    # 1. 언어 설정
    st.markdown("### 1. 🎯 목표 언어 설정 (Target Language)")
    selected_lang = st.selectbox(
        "번역 결과로 출력될 언어를 선택하세요 (Select target output language):",
        list(TEXTS.keys()),
        index=list(TEXTS.keys()).index(st.session_state.target_lang) if st.session_state.target_lang in TEXTS else 0
    )
    
    # 언어가 변경되면 즉시 반영되도록 세션 저장 후 리프레시
    if selected_lang != st.session_state.target_lang:
        st.session_state.target_lang = selected_lang
        st.rerun()

    st.divider()

    # 선택된 언어에 맞는 가이드라인 제목 및 본문 동적 출력
    t_current = TEXTS[selected_lang]
    st.markdown(f"### 2. {t_current['guide_title']}")
    st.info(t_current['guide_content'])

    st.divider()

    # 3. 시작하기 버튼
    if st.button(t_current['start_btn'], use_container_width=True):
        st.session_state.started = True
        st.rerun()

# ---------------------------------------------------------
# [2단계] 메인 번역 화면 (시작하기 클릭 후)
# ---------------------------------------------------------
else:
    st.title(t['title'])
    
    # 사이드바 설정
    st.sidebar.title(t['sidebar_title'])
    api_key = st.sidebar.text_input(t['api_input'], type="password")
    
    st.sidebar.markdown(f"**{t['current_lang']}**\n`{st.session_state.target_lang}`")
    
    if st.sidebar.button(t['back_btn']):
        st.session_state.started = False
        st.rerun()

    st.divider()

    # 번역 탭 구별
    tab1, tab2 = st.tabs([t['tab1'], t['tab2']])

    # --- [탭 1: 텍스트 번역] ---
    with tab1:
        st.header(t['text_header'])
        user_text = st.text_area(t['text_prompt'], height=180)
        
        if st.button(t['text_btn'], use_container_width=True):
            if not api_key:
                st.warning(t['warning_api'])
            elif not user_text.strip():
                st.warning(t['warning_text'])
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    lang_name = st.session_state.target_lang
                    prompt = f"Translate the following text naturally and accurately into {lang_name}:\n\n{user_text}"
                    
                    with st.spinner(t['spinner_text']):
                        response = model.generate_content(prompt)
                        
                    st.success(t['success_res'])
                    st.write(response.text)
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
                    st.warning(t['warning_api'])
                else:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        
                        lang_name = st.session_state.target_lang
                        prompt = f"Extract all text from this image and accurately translate the extracted content into {lang_name}. Output the result clearly separating [Extracted Text] and [Translation Result]."
                        
                        with st.spinner(t['spinner_img']):
                            response = model.generate_content([prompt, image])
                            
                        st.success(t['success_img'])
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"{t['error_msg']}{e}")
