import feedparser

# 테스트 url
# https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER
# https://www.yonhapnewstv.co.kr/category/news/economy/feed/
url = "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER"


# def get_rss_data(url):
#     feed = feedparser.parse(url)
#     news_list = feed.entries[:10]

#     result_list = []

#     # title, link, summarty, author, updated는 바로 사용가능 + updated_parsed
#     for news in news_list:
#         title = news.title
#         link = news.link
#         summary = news.summary
#         author = news.author
#         updated_parsed = news.updated_parsed
#         news_dict = { "title": title, "link": link, "summary": summary, "author": author, "updated_parsed": updated_parsed }
#         result_list.append(news_dict)
        
#     return result_list

def get_oil_news(url):
    feed = feedparser.parse(url)
    news_list = feed.entries[:10]

    with open('./test_new.txt','w', encoding='utf-8-sig') as f :
        f.write(str(news_list))
    print(news_list)

get_oil_news(url)

# 'title' 'link' 'published_parsed' 'author' 'summary' 'tags'[n]['term']