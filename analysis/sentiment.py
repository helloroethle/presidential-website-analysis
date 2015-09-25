import nltk
import textutility
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
from pattern.en import sentiment as patternsent
class Sentiment(object):
  negation_words = ["no", "not", "nobody", "nowhere", "neither", "cannot", "never", "without", "nothing", "no one", "none", "barely", "hardly", "rarely", "no longer", "no more", "no way", "no where", "by no means", "at no time", "not anymore"]
  #not doing anything with stops right now. look into!
  english_stops = set(nltk.corpus.stopwords.words('english'))
  # [word for word in words if word not in english_stops]
  def __init__(self, text, entities):
    self.entities = [w.lower() for w in entities]
    self.text = text
    self.total_scores = {'positive':0, 'negative':0, 'objective':0, 'subjective':0, 'aggregate':0, 'by_sentences':[], 'by_entity':{}}
    self.calculate_sentiment()
  def calculate_sentiment(self):
    sentence_positive = 0
    sentence_negative = 0
    sentence_objective = 0
    sentence_subjective = 0
    sentence_total = 0
    sentence_sentiments = []
    entity_sentiments = {}
    for entity in self.entities:
      entity_sentiments[entity] = 0
    #build sentiment score
    past_words = []
    article_sentences = textutility.sentence_tokenize(self.text)
    pos_tokens = textutility.pos_tag(article_sentences)
    for idx, sentence_token in enumerate(pos_tokens):
      sentence_words = textutility.get_lowercase(textutility.get_words(article_sentences[idx]))
      # The pattern.en sentiment() function returns a (polarity, subjectivity)-tuple for the given sentence, based on the adjectives it contains, where polarity is a value between -1.0 and +1.0 and subjectivity between 0.0 and 1.0.
      patternsent(article_sentences[idx])
      for token in sentence_token:
        word = token[0].strip()
        if word in self.english_stops:
          continue;
        sanitized = self.wordnet_sanitize(token[0], token[1])
        if(sanitized[1] is None):
          word_synset = wn.synsets(sanitized[0])
        else:
          word_synset = wn.synsets(sanitized[0], sanitized[1])
        if word_synset:
          word_synset = word_synset[0]
          sentiment_synset = swn.senti_synset(word_synset.name())
          if sentiment_synset:
            sentence_total = ((sentiment_synset.pos_score() - sentiment_synset.neg_score()) * (1 - sentiment_synset.obj_score())) #weight subjective words
            if(True in past_words):
              sentence_positive += sentiment_synset.neg_score()
              sentence_negative += sentiment_synset.pos_score()
              sentence_total = sentence_total*-1
            else:
              sentence_positive += sentiment_synset.pos_score()
              sentence_negative += sentiment_synset.neg_score()
            sentence_objective += sentiment_synset.obj_score()
            sentence_subjective += (1 - sentiment_synset.obj_score())
        negation = False    
        if(word in self.negation_words or (len(word) > 2 and word[-3:] == "n't")):
          negation = True
        past_words.append(negation)
        if(len(past_words) > 3):
          past_words.pop(0)
      self.total_scores['positive'] += sentence_positive
      self.total_scores['negative'] += sentence_negative
      self.total_scores['objective'] += sentence_objective
      self.total_scores['subjective'] += sentence_subjective
      self.total_scores['aggregate'] += sentence_total
      sentence_sentiments.append(sentence_total)
      for entity in self.entities:
        if entity in sentence_words:
          entity_sentiments[entity] += sentence_total
      sentence_positive = 0
      sentence_negative = 0
      sentence_objective = 0
      sentence_subjective = 0
      sentence_total = 0
    self.total_scores['by_sentences'] = sentence_sentiments
    # self.total_scores['by_entity'] = entity_sentiments
  def wordnet_sanitize(self, string, tag):
      string = string.lower()
      tag = tag.lower()
      #Verb
      if tag.startswith('v'):    
        tag = 'v'
      #Noun
      elif tag.startswith('n'):  
        tag = 'n'
      #Adj
      elif tag.startswith('j'):  
        tag = 'a'
      #Adv
      elif tag.startswith('rb'): 
        tag = 'r'
      if tag in ('a', 'n', 'r', 'v'):
        return (string, tag)
      else:
        return (string, None)
def all_possible_synonyms(self, word, pos):
    synonyms = []
    word = word.strip()
    sanitized = self.wordnet_sanitize(word, pos)
    if(sanitized[1] is None):
      word_synset = wn.synsets(sanitized[0])
    else:
      word_synset = wn.synsets(sanitized[0], sanitized[1])
    for syn in word_synset:
      for lemma in syn.lemmas():
        synonyms.append(lemma.name())
    return synonyms