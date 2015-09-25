import textutility
from sentiment import Sentiment
import pymongo
import json
import datetime
from readability_text_analyzer import *

class NewsItem(object):
    def __init__(self, candidate, title, text, published, href, summary):
        self.candidate = candidate
        self.title = title
        self.text = text
        self.published = published
        self.href = href
        self.summary = summary
        self.sentiment_analysis = {}
        self.readability = textanalyzer()
    def __init__(self, articleDict):
        self.candidate = articleDict.get('candidate')
        self.title = articleDict.get('title')
        self.text = articleDict.get('text')
        self.published = articleDict.get('pubslished')
        self.href = articleDict.get('href')
        self.summary  = articleDict.get('summary')
        self.sentiment_analysis = {}
        self.readability = textanalyzer()
    def sentimentalize(self):
        entities = self.person_entities + self.organization_entities
        sentiment = Sentiment(self.text, entities)
        sentiment_score = sentiment.total_scores
        self.sentiment_analysis['positive'] = sentiment_score.get('positive')
        self.sentiment_analysis['negative'] = sentiment_score.get('negative')
        self.sentiment_analysis['objective'] = sentiment_score.get('objective')
        self.sentiment_analysis['subjective'] = sentiment_score.get('subjective')
        self.sentiment_analysis['total'] = sentiment_score.get('aggregate')
        self.sentiment_analysis['by_sentences'] = sentiment_score.get('by_sentences')
        self.sentiment_analysis['by_entity'] = sentiment_score.get('by_entity')
        self.sentence_sentiment_score()
        self.entity_sentiment_score()
        if self.sentiment_analysis['total'] >= 0:
            self.document_sentiment_classification = 1
        else:
            self.document_sentiment_classification = 0

    # should add a neutral category. Some check if a certain percentage of all sentences are neutral
    def sentence_sentiment_score(self):
        positive_count = len([x for x in self.sentiment_analysis['by_sentences'] if x > 0])
        neutral_count = len([x for x in self.sentiment_analysis['by_sentences'] if x == 0])
        negative_count = len(self.sentiment_analysis['by_sentences']) - positive_count - neutral_count
        if positive_count > negative_count:
            self.sentence_sentiment_classification = 1
        else:
            self.sentence_sentiment_classification = 0

    def entity_sentiment_score(self):
        positive_count = len([x for x in self.sentiment_analysis['by_entity'] if x > 0])
        neutral_count = len([x for x in self.sentiment_analysis['by_entity'] if x == 0])
        negative_count = len(self.sentiment_analysis['by_entity']) - positive_count - neutral_count
        if positive_count > negative_count:
            self.entity_sentiment_classification = 1
        else:
            self.entity_sentiment_classification = 0

    def run_text_analysis(self):
        self.word_distribution = textutility.get_word_distribution(self.text)
        self.unigrams = self.word_distribution.keys()[:100]
        self.bigrams = textutility.get_bigram_collocation(self.text)
        self.trigrams = textutility.get_trigram_collocation(self.text)
        self.length = len(textutility.get_words(self.text))
        self.unique_length = len(textutility.unique_words(self.text))
        self.person_entities = textutility.get_person_entities(self.text)
        self.location_entities = textutility.get_location_entities(self.text)
        self.organization_entities = textutility.get_organization_entities(self.text)
        self.all_named_entities = textutility.get_all_named_entities(self.text)

    def print_analysis(self):
        print self.candidate
        print self.title
        print self.href
        print self.length
        print self.unique_length
        print '_______________________'
        print '# 20 Most Common Words #'
        print self.word_distribution.most_common(50)
        print '# BIGRAMS #'
        print self.bigrams
        print '# TRIGRAMS #'
        print self.trigrams
        print '# Sentiment #'
        print self.sentiment_analysis
        print '# Readability #'
        print self.readability.analyzeText(self.text)
        print '# Person Entities #'
        print self.person_entities
        print '# Location Entities #'
        print self.location_entities
        print '# Organization Entities #'
        print self.organization_entities
        print '# all named entities #'
        print self.all_named_entities

