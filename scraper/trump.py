from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
count = 0
linksToFollow = []
baseURL = 'http://www.donaldjtrump.com/'
extension = 'news'
currentURL = baseURL + extension
while(count < 70):
    print currentURL
    r = requests.get(currentURL)
    soup = BeautifulSoup(r.text,"html.parser")
    soup = soup.select_one('section.main')
    articles = soup.find_all('article', 'press_item')
    for article in articles:
        title = article.select_one('h2')
        href = article.select_one('h2 a')
        source = article.select('p')[0]
        summary = article.select('p')[1]
        published = article.select_one('h6')
        linksToFollow.append({
            'title': title.get_text() if title else '',
            'href' : href.get('href') if href else '',
            'summary' : summary.get_text() if summary else '',
            'published' : published.get_text() if published else '',
            'source' : source.get_text(),
            'candidate' : 'Donalt Trump'
        })
    count+=1
    extension = 'news/P' + str(count*6) 
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
    text = soup.select('article div.content p')
    if len(text) > 0:
        for paragraph in text:
            all_text += paragraph.get_text() + ' '
    if(all_text and len(all_text) > 0):
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : all_text} } )