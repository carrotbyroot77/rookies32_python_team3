import feedparser
import time

# 테스트 url
# https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER
# https://www.yonhapnewstv.co.kr/category/news/economy/feed/
url1 = "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER"
url2 = 'https://www.yonhapnewstv.co.kr/category/news/economy/feed/'

# 'title' 'link' 'published_parsed' 'author' 'summary' 'tags'[n]['term'] 'credit'
def get_oil_news_sbs(url):
    feed = feedparser.parse(url)
    news_list = feed.entries[:500]

    result_url = []

    for news in news_list:
        title = news.title
        link = news.link
        summary = news.summary
        author = news.author
        published_parsed = news.published_parsed
        tags = news.tags
        credit = news.credit
        news_id = news.id[-11:]
        news_dict = { "title": title, "link": link, "summary": summary, "author": author, "published_parsed": time.strftime('%Y-%m-%d %H:%M:%S',published_parsed) ,"tags" : list(set(tag['term'] for tag in tags)), 'credit' : credit}

        if '석유' in news_dict["title"] or '석유' in news_dict['tags']:
            result_url.append(news_dict)

    return result_url

# 'title' 'link' 'published_parsed' 'author' 'tags' 'summary'
def get_oil_news_yonhap(url):
    feed = feedparser.parse(url)
    news_list = feed.entries[:500]

    result_url = []

    for news in news_list:
        title = news.title
        link = news.link
        summary = news.summary
        author = news.author
        published_parsed = news.published_parsed
        tags = news.tags
        credit = '연합뉴스TV'
        news_id = news.id
        news_dict = { "title": title, "link": link, "summary": summary, "author": author, "published_parsed": time.strftime('%Y-%m-%d %H:%M:%S',published_parsed) ,"tags" : list(set(tag['term'] for tag in tags)), 'credit' : credit}

        if '석유' in news_dict['title'] : 
            result_url.append(news_dict)

    return result_url


if __name__ == "__main__":
    print(get_oil_news_sbs(url1))
    print(get_oil_news_yonhap(url2))
