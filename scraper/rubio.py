from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
count = 1
linksToFollow = []
baseURL = 'https://marcorubio.com/category/news/'
extension = ''
currentURL = baseURL + extension
while(count <= 29):
    print currentURL
    r = requests.get(currentURL)
    soup = BeautifulSoup(r.text,"html.parser")
    soup = soup.select_one('main.content')
    articles = soup.find_all('article')
    for article in articles:
        title = article.select_one('header h2')
        href = article.select_one('header h2 a')
        summary = article.select_one('div.entry-content p')
        linksToFollow.append({
            'title': title.get_text() if title else '',
            'href' : href.get('href') if href else '',
            'summary' : summary.get_text() if summary else '',
            'candidate' : 'Marco Rubio'
        })
    count+=1
    extension = 'page/' + str(count) + '/'
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
    text = soup.select('main.content div.entry-content p')
    if len(text) > 0:
        for paragraph in text:
            all_text += paragraph.get_text() + ' '
    if(all_text and len(all_text) > 0):
        pages.update_one( {'_id': link.get('_id')}, { '$set' : {'text' : all_text} } )