import feedparser
import time

# 테스트 url
# https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER
# https://www.yonhapnewstv.co.kr/category/news/economy/feed/
url = "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER"

def get_oil_news_sbs(url):
    feed = feedparser.parse(url)
    news_list = feed.entries[:30]

    result_url = []

    for news in news_list:
        title = news.title
        link = news.link
        summary = news.summary
        author = news.author
        published_parsed = news.published_parsed
        tags = news.tags
        news_dict = { "title": title, "link": link, "summary": summary, "author": author, "published_parsed": time.strftime('%Y-%m-%d %H:%M:%S',published_parsed) ,"tags" : list(set(tag['term'] for tag in tags))}

        if '석유' in news_dict["title"] or '석유' in news_dict['tags']:
            result_url.append(news_dict)

    return result_url

if __name__ == "__main__":
    print(get_oil_news_sbs(url))

# 'title' 'link' 'published_parsed' 'author' 'summary' 'tags'[n]['term'] 'credit'