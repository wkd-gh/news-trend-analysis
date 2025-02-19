import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import datetime
import os

# ✅ NLTK 감성 분석기 다운로드 및 초기화
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

# 네이버 뉴스 크롤링 함수
def get_naver_news():
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ 요청 실패: 상태 코드 {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for item in soup.select("div.list_content a"):
        title = item.get_text().strip()
        link = "https://" + item["href"][7:]
        sentiment_score = sia.polarity_scores(title)["compound"]
        sentiment = "긍정" if sentiment_score > 0 else "부정" if sentiment_score < 0 else "중립"

        articles.append({"title": title, "link": link, "sentiment": sentiment})

    if len(articles) == 0:
        print("❌ 크롤링된 뉴스가 없습니다. 사이트 구조가 변경되었을 가능성이 있습니다.")
    else:
        print(f"✅ 크롤링 완료! 총 {len(articles)}개의 뉴스 수집됨.")

    return articles

# 데이터 저장
def save_to_csv(data):
    if len(data) == 0:
        print("🚨 저장할 뉴스 데이터가 없습니다. CSV 파일을 만들지 않습니다.")
        return None

    df = pd.DataFrame(data)
    today = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"news_{today}.csv"
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"✅ 저장 완료: {filename}")
    return filename

# ✅ README.md 업데이트 함수
def update_readme(news_data):
    if len(news_data) == 0:
        print("🚨 README.md를 업데이트할 뉴스 데이터가 없습니다.")
        return

    today = datetime.date.today().strftime("%Y-%m-%d")

    # ✅ 감성 분석 결과 요약
    sentiment_counts = {"긍정": 0, "부정": 0, "중립": 0}
    for news in news_data:
        sentiment_counts[news["sentiment"]] += 1

    sentiment_summary = (
        f"🟢 긍정 뉴스: {sentiment_counts['긍정']}개 | 🔴 부정 뉴스: {sentiment_counts['부정']}개 | ⚪ 중립 뉴스: {sentiment_counts['중립']}개"
    )

    # ✅ 최신 뉴스 5개만 선택
    latest_news = news_data[:5]

    # ✅ Markdown 테이블 생성
    # news_table = "| No | Headline | Sentiment |\n|----|---------|----------|\n"
    # for i, news in enumerate(latest_news, 1):
    #     sentiment_icon = "😊" if news["sentiment"] == "긍정" else "😡" if news["sentiment"] == "부정" else "😐"
    #     news_table += f"| {i} | [{news['title']}]({news['link']}) | {sentiment_icon} {news['sentiment']} |\n"
    
    # ✅ Markdown 테이블 생성 (파이프 문자 `|`를 안전하게 변환)
    news_table = "| No | Headline | Sentiment |\n|----|---------|----------|\n"
    for i, news in enumerate(latest_news, 1):
        safe_title = news['title'].replace("|", "｜")  # 🛠️ `|`를 `｜`(전각 문자)로 변환하여 Markdown 충돌 방지
        sentiment_icon = "😊" if news["sentiment"] == "긍정" else "😡" if news["sentiment"] == "부정" else "😐"
        news_table += f"| {i} | [{safe_title}]({news['link']}) | {sentiment_icon} {news['sentiment']} |\n"

    # ✅ README.md 업데이트 (최신 뉴스만 유지)
    readme_content = f"""# 📰 News Trend Analysis

    🚀 This project automatically scrapes the latest news daily and updates this repository.

    ## 📅 Latest News ({today})

    **{sentiment_summary}**

    {news_table}

    📜 **[View Full News Archive](news_archive.md)** 👈 (Click here for past news)
    """

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("✅ README.md updated successfully!")

    # ✅ 과거 뉴스 기록을 `news_archive.md`에 저장
    archive_file = "news_archive.md"
    archive_entry = f"## 📅 {today}\n\n{news_table}\n---\n"

    if os.path.exists(archive_file):
        with open(archive_file, "r", encoding="utf-8") as f:
            old_archive = f.read()
    else:
        old_archive = "# 📜 News Archive\n\n"

    with open(archive_file, "w", encoding="utf-8") as f:
        f.write(old_archive + archive_entry)

    print("✅ news_archive.md updated successfully!")

if __name__ == "__main__":
    news = get_naver_news()
    save_to_csv(news)
    update_readme(news)