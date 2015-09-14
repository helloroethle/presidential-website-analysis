from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
count = 1
linksToFollow = []
baseURL = 'https://www.bencarson.com/news/news-updates'
extension = ''
currentURL = baseURL + extension
while(count <= 6):
    print currentURL
    r = requests.get(currentURL)
    soup = BeautifulSoup(r.text,"html.parser")
    soup = soup.select_one('section.main-content__article')
    articles = soup.find_all('article')
    for article in articles:
        title = article.select_one('h1')
        href = article.select_one('h1 a')
        summary = article.select_one('p')
        published = article.select_one('date')
        linksToFollow.append({
            'title': title.get_text() if title else '',
            'href' : 'http:' + href.get('href') if href else '',
            'summary' : summary.get_text() if summary else '',
            'published' : published.get_text() if published else '',
            'candidate' : 'Ben Carson'
        })
    count+=1
    extension = '/page/' + str(count)
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
    text = soup.select('div.post__body p')
    if len(text) > 0:
        for paragraph in text:
            all_text += paragraph.get_text() + ' '
    if(all_text and len(all_text) > 0):
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : all_text} } )