import streamlit as st

# 1. 모바일 앱 환경에 최적화된 레이아웃 설정
st.set_page_config(
    page_title="KHU Global Helper",
    page_icon="🎓",
    layout="centered"
)

# 2. 앱 타이틀 및 헤더
st.title("🎓 KHU All-in-One Academic Translator")
st.markdown("### e-Campus & Notice Translator for International Students")
st.caption("경희대 유학생을 위한 학사 공지사항 올인원 번역 및 요약 툴")

st.divider()

# 3. 입력 섹션 (이미지 업로드)
st.subheader("1. Upload Notice Image")
uploaded_file = st.file_uploader("e-Campus 공지사항/강의실 안내 캡처본을 업로드하세요", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="업로드된 공지사항 이미지", use_container_width=True)
else:
    st.info("💡 캡처 이미지가 없다면 아래 버튼을 눌러 바로 실험해 볼 수 있습니다!")

# 4. 타겟 언어 선택
st.subheader("2. Select Target Language")
target_lang = st.selectbox(
    "번역할 언어를 선택하세요", 
    ["English", "Russian (Русский)", "Spanish (Español)", "Chinese (中文)"]
)

st.divider()

# 5. 올인원 실행 버튼 및 결과 카드 출력
if st.button("🚀 Run All-in-One Translation & Summary", use_container_width=True):
    with st.spinner("Processing OCR & Academic Glossary Matching..."):
        # 시연용 로딩 연출 (0.8초 대기)
        import time
        time.sleep(0.8)
        
    st.success("✅ All-in-One Processing Complete!")
    
    # 올인원 구조화 요약 카드 UI
    st.markdown("### 📋 All-in-One Summary Card")
    st.info(f"**Target Language:** {target_lang}")
    
    # 선택된 언어에 맞춰 동적으로 보여지는 시연 데이터
    if "English" in target_lang:
        st.markdown("""
        #### 📌 Summary
        - Guidelines for **Course Withdrawal (드롭)** and final registration for the semester.

        #### 📅 Key Deadlines & Dates
        - **Course Drop Period:** Until this Friday, 18:00 KST
        - **Target Students:** Department of Industrial and Management Engineering (산경공)

        #### 📍 Location / Building
        - **Venue:** Cheongwoon Hall (청운관) B101
        
        #### 📖 Kyung Hee Academic Glossary Applied
        - **드롭** $\rightarrow$ Course Withdrawal
        - **산경공** $\rightarrow$ Dept. of Industrial and Management Engineering
        - **전자출결** $\rightarrow$ Mobile E-Attendance System
        """)
    elif "Russian" in target_lang:
        st.markdown("""
        #### 📌 Summary (Резюме)
        - Руководство по **отмене курсов (드롭)** и регистрации на семестр.

        #### 📅 Key Deadlines & Dates
        - **Период отмены:** До пятницы, 18:00
        - **Цель:** Студенты факультета промышленного менеджмента (산경공)

        #### 📍 Location / Building
        - **Место:** Корпус Чхонун (청운관) B101
        
        #### 📖 Glossary Applied
        - **드롭** $\rightarrow$ Отмена курса (Course Withdrawal)
        - **청운관** $\rightarrow$ Корпус Чхонун (Cheongwoon Hall)
        """)
    else:
        st.markdown("""
        #### 📌 Summary
        - Guidelines for course withdrawal and academic schedule.

        #### 📅 Key Deadlines & Dates
        - **Deadline:** This Friday 18:00

        #### 📍 Location / Building
        - **Venue:** Cheongwoon Hall (청운관) B101
        
        #### 📖 Glossary Applied
        - **드롭** $\rightarrow$ Course Withdrawal
        - **청운관** $\rightarrow$ Cheongwoon Hall
        """)