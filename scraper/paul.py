from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
linksToFollow = []
soup = BeautifulSoup(open("paul-news-full.html"), 'html.parser')
soup = soup.select_one('section.news-area')
articles = soup.find_all('div', 'm-star')
for article in articles:
    title = article.select_one('h4')
    href = article.select_one('h4 a')
    summary = article.select_one('p')
    published = article.select_one('span.date')
    linksToFollow.append({
        'title': title.get_text() if title else '',
        'href' : href.get('href') if href else '',
        'summary' : summary.get_text() if summary else '',
        'published' : published.get_text() if published else '',
        'candidate' : 'Rand Paul'
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
    text = soup.select_one('div.article-text')
    text = text.get_text() if text else ''
    if(text and len(text) > 0):
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : text} } )