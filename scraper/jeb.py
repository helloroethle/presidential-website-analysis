from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
linksToFollow = []
soup = BeautifulSoup(open("jeb-news-full.html"), 'html.parser')
soup = soup.select_one('div.main-content')
top_news_articles = soup.find_all('div', 'top-news')
news_articles = soup.find_all('div', 'news-table')
for article_container in news_articles:
    articles = article_container.find_all('article')
    for article in articles:
        title = article.select_one('header a h2')
        href = article.select_one('header a')
        summary = article.select_one('div.language-swappable p')
        linksToFollow.append({
            'title': title.get_text() if title else '',
            'href' : href.get('href') if href else '',
            'summary' : summary.get_text() if summary else '',
            'candidate' : 'Jeb Bush'
        })

for article in top_news_articles:
    title = article.select_one('header a h2')
    href = article.select_one('header a')
    summary = article.select_one('div.language-swappable p')
    linksToFollow.append({
        'title': title.get_text() if title else '',
        'href' : href.get('href') if href else '',
        'summary' : summary.get_text() if summary else '',
        'candidate' : 'Jeb Bush'
    })

for link in linksToFollow:
    if pages.find_one({'href' : link.get('href')}):
        link['noprocess'] = True
        print link.get('href')
    else:
        link['_id'] = pages.insert_one(link).inserted_id
for link in linksToFollow:
    if link.get('noprocess'):
        continue
    r = requests.get(link.get('href'))
    soup = BeautifulSoup(r.text,"html.parser")
    text = soup.select_one('section.entry-content')
    text = text.get_text() if text else ''
    if(text and len(text) > 0):
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : text} } )