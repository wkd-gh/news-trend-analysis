import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import datetime

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

if __name__ == "__main__":
    news = get_naver_news()
    save_to_csv(news)
