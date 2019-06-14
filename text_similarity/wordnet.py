#import nltk
#nltk.download('wordnet_ic')

#nltk.download('averaged_perceptron_tagger')
#nltk.download('punkt')
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from nltk import word_tokenize, pos_tag
from tfidf import TFIDF
from functools import reduce
import spacy

brown_ic = wordnet_ic.ic('ic-brown.dat') #load the brown corpus to compute the IC

class WordNetSimilarity:
    """"""
    
    def __init__(self, intents, focus_sent):
        self.nlp = spacy.load('en_core_web_sm')
        self.compute_idf(intents, focus_sent)

    def compute_idf(self, intents, focus_sent):
        t = TFIDF(intents)
        t.compute_similarity(focus_sent)
        self.idf = t.idf
        self.vocabulary = t.vocabulary
    

    def tag_to_wn(self, tag):
        """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
        if tag.startswith('N'):
            return 'n'
     
        if tag.startswith('V'):
            return 'v'
     
        if tag.startswith('J'):
            return 'a'
     
        if tag.startswith('R'):
            return 'r'
 
        return None  

    def tagged_to_synset(self, word, tag):
        """ Returns the first synset of the word given as parameter"""

        wn_tag = self.tag_to_wn(tag)
        if wn_tag is None:
            return None
     
        try:
            return wn.synsets(word, wn_tag)[0]
        except:
            return None  

    def compute_sim(self, synsets1, synsets2):

        score, idf_sum = 0.0, 0
 
        # For each word in the first sentence
        for w,synset in synsets1:
            # Get the similarity value of the most similar word in the other sentence
            word_idf = self.idf[self.vocabulary[w]]
            best_score = max([0 if synset.path_similarity(ss[1]) is None else synset.path_similarity(ss[1]) for ss in synsets2]) * word_idf
            
            score += best_score
            idf_sum += word_idf
     
        # Average the values
        score /= idf_sum
        return score

    def sentence_similarity(self, sentence1, sentence2):
        """ compute the sentence similarity using Wordnet """

        # Tokenize and tag
        sentence1 = pos_tag(word_tokenize(sentence1.lower()))
        sentence2 = pos_tag(word_tokenize(sentence2.lower()))
 

        
        # Get the synsets for the tagged words
        # Filter out the Nones
        synsets1 = reduce(lambda acc, w: acc if self.tagged_to_synset(*w) is None else acc + [(w[0], self.tagged_to_synset(*w))], sentence1, [])
        synsets2 = reduce(lambda acc, w: acc if self.tagged_to_synset(*w) is None else acc + [(w[0], self.tagged_to_synset(*w))], sentence2, [])
       
        return (self.compute_sim(synsets1, synsets2) + self.compute_sim(synsets2, synsets1)) / 2
 


if __name__ == '__main__':


    sentences = [
        "Dogs are awesome.",
        "Some gorgeous creatures are felines.",
        "Dolphins are swimming mammals.",
        "Cats are beautiful animals.",

    ]
 
    focus_sentence = "Some gorgeous creatures are dogs."
    w = WordNetSimilarity(sentences, focus_sentence)
    for sentence in sentences:
        print("Similarity(\"%s\", \"%s\") = %s" % (focus_sentence, sentence, w.sentence_similarity(focus_sentence, sentence)))

