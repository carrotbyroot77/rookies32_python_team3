import feedparser
import time

SBS_URL = "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER"
YONHAP_URL = "https://www.yonhapnewstv.co.kr/category/news/economy/feed/"

KEYWORDS = ['석유', '유가', '기름값', '주유소']


def _parse_entry(entry, credit):
    """공통 뉴스 항목 파싱"""
    title = getattr(entry, 'title', '')
    link = getattr(entry, 'link', '')
    summary = getattr(entry, 'summary', '')
    author = getattr(entry, 'author', '')

    published_parsed = getattr(entry, 'published_parsed', None)
    published = time.strftime('%Y-%m-%d %H:%M:%S', published_parsed) if published_parsed else '날짜 없음'

    raw_tags = getattr(entry, 'tags', [])
    tags = list(set(tag['term'] for tag in raw_tags if 'term' in tag))

    return {
        "title": title,
        "link": link,
        "summary": summary,
        "author": author,
        "published": published,
        "tags": tags,
        "credit": credit
    }


def _is_oil_related(news_dict):
    """석유/유가 관련 뉴스 여부 확인"""
    title = news_dict.get('title', '')
    tags_str = ' '.join(news_dict.get('tags', []))
    return any(kw in title or kw in tags_str for kw in KEYWORDS)


def get_oil_news_sbs(url=SBS_URL):
    feed = feedparser.parse(url)
    result = []
    for entry in feed.entries[:30]:
        news = _parse_entry(entry, credit=getattr(entry, 'credit', 'SBS'))
        if _is_oil_related(news):
            result.append(news)
    return result


def get_oil_news_yonhap(url=YONHAP_URL):
    feed = feedparser.parse(url)
    result = []
    for entry in feed.entries[:20]:
        news = _parse_entry(entry, credit='연합뉴스TV')
        if _is_oil_related(news):
            result.append(news)
    return result


def get_all_oil_news():
    """SBS + 연합뉴스TV 통합 조회, 최신순 정렬"""
    news = get_oil_news_sbs() + get_oil_news_yonhap()
    news.sort(key=lambda x: x['published'], reverse=True)
    return news


if __name__ == "__main__":
    all_news = get_all_oil_news()
    for n in all_news:
        print(f"[{n['credit']}] {n['title']} ({n['published']})")
