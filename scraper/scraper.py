from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
count = 0
linksToFollow = []
baseURL = 'https://www.scottwalker.com'
extension = '/news'
currentURL = baseURL + extension
while(count < 9):
    r = requests.get(currentURL)
    soup = BeautifulSoup(r.text,"html.parser")
    allText = soup.get_text()
    soup = soup.select_one('div#news')
    articles = soup.find_all('article', 'post')
    for article in articles:
        title = article.select_one('header h4')
        extension = article.select_one('header h4 a')
        summary = article.select_one('div.details')
        topics = article.select_one('dl.topics dd ul li')
        linksToFollow.append({
            'title': title.get_text() if title else '',
            'href' : baseURL + extension.get('href') if extension else '',
            'summary' : summary.get_text() if summary else '',
            'topics' : topics.get_text() if topics else '',
            'candidate' : 'Scott Walker'
        })
    count+=1
    print count
    extension = '/news?page=' + str(count)
    currentURL = baseURL + extension
for link in linksToFollow:
    if pages.find_one({'href' : link.get('href')}):
        link['noprocess'] = true
    else:
        link['_id'] = pages.insert_one(link).inserted_id
for link in linksToFollow:
    if link.get('noprocess'):
        continue
    r = requests.get(link.get('href'))
    soup = BeautifulSoup(r.text,"html.parser")
    text = soup.select_one('div#news-article article.post.overview div.details')
    text = text.get_text() if text else ''
    if(text and len(text) > 0):
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : text} } )