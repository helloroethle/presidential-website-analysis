from newsItem import NewsItem
import nltk.corpus
from pymongo import MongoClient
client = MongoClient()
db = client.presidentSites
pages = db.pages
# candidates = ['Bernie Sanders', 'Ben Carson', 'Chris Christie', 'Ted Cruz', 'Hillary Clinton', 'Mike Huckabee', 'Jeb Bush', 'Rand Paul', 'John Kasich', 'Marco Rubio', 'Donalt Trump', 'Scott Walker']
candidates = ['Bernie Sanders']
# candidates = ['Mike Huckabee', 'Jeb Bush', 'Rand Paul']
def run_that_analysis():
  for candidate in candidates:
    candidate_articles = pages.find({ 'candidate': candidate })
    aggregate_article = candidate_articles[0]
    if aggregate_article.get('text') == None:
      aggregate_article['text'] = ''
    for single_article in candidate_articles:
      if single_article.get('text') and len(single_article.get('text')) > 0:
        aggregate_article['text'] = aggregate_article.get('text') + ' ' + single_article.get('text')
    newsItem = NewsItem(aggregate_article)
    newsItem.run_text_analysis()
    newsItem.sentimentalize()
    newsItem.print_analysis()

if __name__ == "__main__":
    run_that_analysis()

