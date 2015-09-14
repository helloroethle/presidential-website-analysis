from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
count = 1
linksToFollow = []
baseURL = 'https://www.chrischristie.com'
extension = '/news?page=1'
currentURL = baseURL + extension
while(count <= 3):
    r = requests.get(currentURL)
    soup = BeautifulSoup(r.text,"html.parser")
    soup = soup.select_one('div#columns')
    articles = soup.find_all('div', 'item')
    for article in articles:
        title = article.select_one('h3')
        href = article.select_one('h3 a')
        summary = article.select_one('div.excerpt p')
        published = article.select_one('div.date')
        linksToFollow.append({
            'title': title.get_text() if title else '',
            'href' : baseURL + href.get('href') if href else '',
            'summary' : summary.get_text() if summary else '',
            'published' : published.get_text() if published else '',
            'candidate' : 'Chris Christie'
        })
    count+=1
    extension = '/news?page=' + str(count)
    currentURL = baseURL + extension
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
    text = soup.select_one('div.content')
    text = text.get_text() if text else ''
    if text and len(text) > 0:
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : text} } )