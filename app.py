# streamlit 실행파일

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
import datetime

# ✅ 한글 폰트 설정 (Windows: 'Malgun Gothic', Mac: 'AppleGothic')
plt.rc('font', family='Malgun Gothic')  # Windows
plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 깨짐 방지

# ✅ 한글 폰트 경로 설정 (Windows 기준)
font_path = "C:/Windows/Fonts/malgun.ttf"

# ✅ 화면 너비 확장 (wide 모드)
st.set_page_config(layout="wide", page_title="뉴스 트렌드 분석", page_icon="📰")

# ✅ 스타일 개선 (Markdown을 활용한 CSS 적용)
st.markdown(
    """
    <style>
        body { background-color: #f8f9fa; }
        .stApp { background-color: white; }
        .main-title { font-size: 36px; font-weight: bold; color: #007bff; text-align: center; }
        .sub-title { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
        .card { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }
        .pagination-container { display: flex; justify-content: center; margin-top: 20px; gap: 5px; }
        .pagination-btn { padding: 8px 12px; background: #f1f1f1; border-radius: 5px; cursor: pointer; font-weight: bold; border: 1px solid #ddd; display: inline-block; }
        .pagination-btn:hover { background: #007bff; color: white; }
        .pagination-active { background: #007bff; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ 현재 날짜
today = datetime.date.today().strftime("%Y-%m-%d")
file_name = f"news_{today}.csv"

# 🔥 뉴스 크롤링 자동 실행 (파일이 없으면 실행)
if not os.path.exists(file_name):
    st.info("📡 뉴스 데이터를 가져오는 중...")
    os.system("python news_scraper.py")  # 자동 실행

# 📌 크롤링한 데이터 불러오기
if os.path.exists(file_name):
    df = pd.read_csv(file_name)

    # ✅ 헤더 디자인
    st.markdown('<h1 class="main-title">📰 뉴스 트렌드 & 감성 분석</h1>', unsafe_allow_html=True)
    st.markdown(f'<h3 class="sub-title">📅 오늘 ({today})의 뉴스 트렌드</h3>', unsafe_allow_html=True)

    # ✅ 레이아웃 구성 (감성 분석 차트 & 워드 클라우드 나란히 배치)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card"><h3 class="sub-title">📊 감성 분석 결과</h3>', unsafe_allow_html=True)
        sentiment_counts = df["sentiment"].value_counts()

        # ✅ 감성 분석 원형 그래프 스타일 개선
        fig, ax = plt.subplots(figsize=(6, 6), facecolor='#f8f9fa')  # 배경색 추가
        colors = ["#4CAF50", "#FF5252", "#FFC107"]  # 긍정(녹색), 부정(빨강), 중립(노랑)
        wedges, texts, autotexts = ax.pie(
            sentiment_counts,
            labels=sentiment_counts.index,
            autopct="%1.1f%%",
            colors=colors,
            wedgeprops={'edgecolor': 'black', 'linewidth': 1.5},
            textprops={'fontsize': 14, 'weight': 'bold'}
        )
        ax.set_title("긍정 vs 부정 vs 중립 뉴스 비율", fontsize=16, fontweight='bold', color='#333')
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><h3 class="sub-title">📢 주요 키워드</h3>', unsafe_allow_html=True)
        text = " ".join(df["title"])
        wordcloud = WordCloud(font_path=font_path, width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ 페이지네이션 설정
    items_per_page = 7  # 한 페이지당 5개 뉴스 표시
    total_pages = -(-len(df) // items_per_page)  # 전체 페이지 수 계산 (올림 처리)

    # ✅ 현재 페이지 상태 관리 (Streamlit Session State 활용)
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    # ✅ 현재 페이지에 해당하는 뉴스만 표시
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    df_page = df.iloc[start_idx:end_idx]

    # ✅ 뉴스 목록 (카드 스타일 적용)
    st.markdown('<div class="card"><h3 class="sub-title">📰 뉴스 목록</h3>', unsafe_allow_html=True)

    for index, row in df_page.iterrows():
        st.markdown(
            f"""
            <div style="padding: 10px; margin-bottom: 10px; background: #f8f9fa; border-left: 5px solid {'#4CAF50' if row['sentiment'] == '긍정' else '#FF5252' if row['sentiment'] == '부정' else '#FFC107'};">
                <h4>{row['title']}</h4>
                <p><a href="{row['link']}" target="_blank">🔗 뉴스 기사 보기</a></p>
                <p><b>감성 분석:</b> {'😊 긍정' if row['sentiment'] == '긍정' else '😡 부정' if row['sentiment'] == '부정' else '😐 중립'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ✅ 페이지네이션 버튼을 하단에 가로 정렬로 표시 (`st.columns()` 활용)
    num_columns = min(22, total_pages)  # 한 줄에 최대 20개 버튼 표시
    cols = st.columns(num_columns)

    for i, page in enumerate(range(1, total_pages + 1)):
        with cols[i % num_columns]:  # 가로 정렬
            if st.button(f"{page}", key=f"page_{page}", help=f"{page} 페이지로 이동"):
                st.session_state.current_page = page
                st.rerun()  # 페이지 변경 시 새로고침

else:
    st.error("🚨 뉴스 데이터를 가져올 수 없습니다. 다시 실행해 주세요.")
