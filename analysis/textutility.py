import re
import nltk
from chunkers import *
from nltk.stem import WordNetLemmatizer
from collections import OrderedDict
# this tokenizer discards punctuation and doesn't split on contractions
word_tokenizer = nltk.tokenize.RegexpTokenizer("[\w']+")
english_stops = set(nltk.corpus.stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
# english_stops.extend("don't", "couldn't", "wouldn't", "shouldn't", "can't")
#more efficient instead of loading tokenizer on demand every time it needs to be used
sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
from nltk.chunk import ne_chunk

# UTILITY METHODS #
def get_words(content):
  return word_tokenizer.tokenize(content)

def get_lowercase(words):
  return [w.lower() for w in words]

def remove_stop_words(words):
  return [word for word in words if word not in english_stops]

def sentence_tokenize(text):
  return sentence_tokenizer.tokenize(text)

def unique_words(text):
  words = get_words(text)
  return set(get_lowercase(words))

# find the root of the word given the part of speech
def lemmatize(word, pos):
  return lemmatizer.lemmatize(word, pos=pos)

def save_tagger_to_pickle(tagger, filename):
    import pickle
    f = open(filename, 'wb')
    pickle.dump(tagger, f)
    f.close()

def load_tagger_from_pickle(filename):
    f = open(filename, 'rb')
    return pickle.load(f)

def replace_contractions(content):
    replacement_patterns = [
        (r'won\'t', 'will not'),
        (r'can\'t', 'cannot'),
        (r'i\'m', 'i am'),
        (r'ain\'t', 'is not'),
        (r'(\w+)\'ll', '\g<1> will'),
        (r'(\w+)n\'t', '\g<1> not'),
        (r'(\w+)\'ve', '\g<1> have'),
        (r'(\w+)\'s', '\g<1> is'),
        (r'(\w+)\'re', '\g<1> are'),
        (r'(\w+)\'d', '\g<1> would')
    ]
    replacement_patterns = [(re.compile(regex), repl) for (regex, repl) in replacement_patterns]
    text = content
    for (pattern, repl) in replacement_patterns:
        text = re.sub(pattern, repl, text)
    return text


# COLLOCATION AND DISTRIBUTIONS #
def get_word_distribution(content):
    words = get_words(content)
    words = get_lowercase(words)
    words = remove_stop_words(words)
    word_fdist = nltk.FreqDist(words)
    return word_fdist

#returns a list of bigram tuples
def get_bigram_collocation(content):
    words = get_words(content)
    words = get_lowercase(words)
    filter_stops = lambda w: len(w) < 3 or w in english_stops
    bcf = nltk.collocations.BigramCollocationFinder.from_words(words)
    bcf.apply_word_filter(filter_stops)
    bcf.apply_freq_filter(2) # Must occur at least 2 times to be considered
    return bcf.nbest(nltk.metrics.BigramAssocMeasures.likelihood_ratio, 40) # takes the 10 most common bigrams - can change this number

#returns a list of trigram tuples
def get_trigram_collocation(content):
    words = get_words(content)
    words = get_lowercase(words)
    filter_stops = lambda w: len(w) < 3 or w in english_stops
    tcf = nltk.collocations.TrigramCollocationFinder.from_words(words)
    tcf.apply_word_filter(filter_stops)
    tcf.apply_freq_filter(2) # Must occur at least 2 times to be considered
    return tcf.nbest(nltk.metrics.TrigramAssocMeasures.likelihood_ratio, 20) #takes the 4 most common trigrams - can change this number

# TAGGERS AND CHUNKERS # 
# by default, the ClassifierBasedPOSTager uses NaiveBayesClassification and it uses the word net tagger as a backoff trainer
def train_pos_tager():
    wt = WordNetTagger()
    train_sents = nltk.corpus.treebank.tagged_sents()
    tagger = nltk.tag.sequential.ClassifierBasedPOSTagger(train=train_sents, backoff=wt, cutoff_prob=0.3)
    return tagger

def train_chunker():
    conll_train = nltk.corpus.conll2000.chunked_sents('train.txt')
    chunker = ClassifierChunker(conll_train)
    return chunker

def pos_tag(article_sentences):    
  #maybe add a check that it is indeed an iterable of sentences
  pos_tokens = []
  pos_tagger = train_pos_tager()
  for sentence in article_sentences:
    sentence_tokens = word_tokenizer.tokenize(sentence)
    pos_tokens.append(pos_tagger.tag(sentence_tokens))
  return pos_tokens

# conll2000 training set
def chunk_tag(sentence_pos_tokens):
    chunker = train_chunker()
    sentence_chunk_trees = []
    for sentence_tokens in sentence_pos_tokens:
        chunked = chunker.parse(sentence_tokens)
        if chunked:
            sentence_chunk_trees.append(chunked)
    return sentence_chunk_trees

# EVALUATION #
def evaluate_pos_tagger(tagger):
    test_sents = nltk.corpus.treebank.tagged_sents()[3000:]
    print tagger.evaluate(test_sents)

def evaluate_chunker(chunker):
  test_chunks = ntlk.corpus.treebank_chunk.chunked_sents()[3000:]
  score = chunker.evaluate(test_chunks)
  print score.accuracy()
  print score.precision()
  print score.recall()


# NOUN PHRASES AND ENTITY EXTRACTION #
def get_person_entities(content):
    pos_sentences_tokens = prep_named_entities(content)
    named_entities = []
    people = []
    for pos_tree in pos_sentences_tokens:
        ne_chunk_tree = ne_chunk(pos_tree)
        leaves = sub_leaves(ne_chunk_tree, 'PERSON')
        if leaves:
          named_entities.append(leaves)
    for sentence_entities in named_entities:
      for entity in sentence_entities:
        people.append(' '.join([name[0] for name in entity]))
    return list(OrderedDict.fromkeys(people))

def get_organization_entities(content):
    pos_sentences_tokens = prep_named_entities(content)
    named_entities = []
    organizations = []
    for pos_tree in pos_sentences_tokens:
        ne_chunk_tree = ne_chunk(pos_tree)
        leaves = sub_leaves(ne_chunk_tree, 'ORGANIZATION')
        if leaves:
          named_entities.append(leaves)
    for sentence_entities in named_entities:
      for entity in sentence_entities:
        organizations.append(' '.join([name[0] for name in entity]))
    return list(OrderedDict.fromkeys(organizations))

def get_location_entities(content):
    pos_sentences_tokens = prep_named_entities(content)
    named_entities = []
    locations = []
    for pos_tree in pos_sentences_tokens:
        ne_chunk_tree = ne_chunk(pos_tree)
        leaves = sub_leaves(ne_chunk_tree, 'GPE')
        if leaves:
          named_entities.append(leaves)
    for sentence_entities in named_entities:
      for entity in sentence_entities:
        locations.append(' '.join([name[0] for name in entity]))
    return list(OrderedDict.fromkeys(locations))

def prep_named_entities(content):
    article_sentences = sentence_tokenize(content)
    return pos_tag(article_sentences)

def get_all_named_entities(content):
    pos_sentences_tokens = prep_named_entities(content)
    named_entities = []
    nouns = []
    for pos_tree in pos_sentences_tokens:
        # binary = True grabs all named entities instead of classifying person, location, etc.
        ne_chunk_tree = ne_chunk(pos_tree, binary=True)
        leaves = sub_leaves(ne_chunk_tree, 'NE')
        if leaves:
          named_entities.append(leaves)
    for sentence_entities in named_entities:
      for entity in sentence_entities:
        nouns.append(' '.join([name[0] for name in entity]))
    return list(OrderedDict.fromkeys(nouns))


# maybe check for existence of "np" or starts with "np"
def sub_leaves(tree, label):
  return [t.leaves() for t in tree.subtrees(lambda s: s.label() == label)]

def extract_noun_phrases(sentence_tree):
  noun_phrases = []
  for sentence in sentence_tree:
    for phrases in sentence:
      phrase_words = ''
      for word in phrases:
        try:
          phrase_words += str(word[0])
        except:
          phrase_words += str(word[0].encode('utf'))
        phrase_words += ' '
      if len(phrase_words) > 3:
        noun_phrases.append(phrase_words.strip())
  return noun_phrases

def build_noun_phrase_tree(sentence_pos_tokens):
    sentence_chunks = chunk_tag(sentence_pos_tokens)
    noun_phrases = []
    for chunk_tree in sentence_chunks:
        noun_phrases.append(sub_leaves(chunk_tree, 'NP'))
    return noun_phrases

def get_noun_phrases(content):
    article_sentences = sentence_tokenize(content)
    pos_sentences_tokens = pos_tag(article_sentences)
    noun_phrase_tree = build_noun_phrase_tree(pos_sentences_tokens)
    noun_phrases = extract_noun_phrases(noun_phrase_tree)
    return noun_phrases

  # '''
  # >>> wt = WordNetTagger()
  # >>> wt.tag(['food', 'is', 'great'])
  # [('food', 'NN'), ('is', 'VB'), ('great', 'JJ')]
  # '''
class WordNetTagger(nltk.tag.SequentialBackoffTagger):
    def __init__(self, *args, **kwargs):
        nltk.tag.SequentialBackoffTagger.__init__(self, *args, **kwargs)
        self.wordnet_tag_map = {
            'n': 'NN',
            's': 'JJ',
            'a': 'JJ',
            'r': 'RB',
            'v': 'VB'
        }
    def choose_tag(self, tokens, index, history):
        word = tokens[index]
        fd = nltk.probability.FreqDist()
        for synset in nltk.corpus.wordnet.synsets(word):
            fd[synset.pos()] += 1
        if not fd: return 'NN' 
        return self.wordnet_tag_map.get(fd.max())
