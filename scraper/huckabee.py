from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
count = 1
linksToFollow = []
baseURL = 'http://mikehuckabee.com'
extension = '/news'
currentURL = baseURL + extension
while(count < 6):
    print currentURL
    r = requests.get(currentURL)
    soup = BeautifulSoup(r.text,"html.parser")
    soup = soup.select_one('div#copy div.recordList')
    articles = soup.find_all('article')
    for article in articles:
        title = article.select_one('h1')
        href = article.select_one('h1 a')
        summary = article.select_one('div.media')
        published = article.select_one('h4 span.date')
        linksToFollow.append({
            'title': title.get_text() if title else '',
            'href' : baseURL + href.get('href') if href else '',
            'summary' : summary.get_text() if summary else '',
            'published' : published.get_text() if published else '',
            'candidate' : 'Mike Huckabee'
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
    all_text = ''
    text = soup.select_one('article.post div.content')
    text = text.get_text() if text else ''
    if(text and len(text) > 0):
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : text} } )