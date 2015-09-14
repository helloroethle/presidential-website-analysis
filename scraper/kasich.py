from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
linksToFollow = []
currentURL = 'https://johnkasich.com/news/'
r = requests.get(currentURL)
soup = BeautifulSoup(r.text,"html.parser")
articles = soup.find_all('article', 'entry')
for article in articles:
    title = article.select_one('h2')
    href = article.select_one('h2 a')
    summary = article.select_one('div.cap p')
    linksToFollow.append({
        'title': title.get_text() if title else '',
        'href' : href.get('href') if href else '',
        'summary' : summary.get_text() if summary else '',
        'candidate' : 'John Kasich'
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
    all_text = ''
    text = soup.select_one('div.post-content')
    text = text.get_text() if text else ''
    if(text and len(text) > 0):
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : text} } )