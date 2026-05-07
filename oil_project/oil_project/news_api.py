import feedparser

# 유가/에너지 관련 RSS 피드
OIL_RSS_URL = "https://www.hankyung.com/feed/economy"


def get_oil_news(url: str = OIL_RSS_URL) -> list:
    """RSS 피드에서 뉴스 목록을 가져와 리스트로 반환

    Args:
        url : RSS 피드 URL (기본값: 한국경제 경제뉴스)

    Returns:
        뉴스 딕셔너리 리스트 (title, link, summary)
    """

    try:
        feed = feedparser.parse(url)
        news_list = feed.entries[:5]

        result_list = []

        for news in news_list:
            title   = news.get("title", "")
            link    = news.get("link", "")
            summary = news.get("summary", "")

            news_dict = {
                "title"   : title,
                "link"    : link,
                "summary" : summary,
            }
            result_list.append(news_dict)

        return result_list

    except Exception as e:
        print(f"뉴스 로드 오류 : {e}")
        return []
