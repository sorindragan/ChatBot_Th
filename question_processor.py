import re
import spacy
from spacy import displacy
from pprint import pprint

from triplet_extractor import TripletExtractor


class QuestionProcessor:

    def __init__(self, phrase):
        self.nlp = spacy.load('en')
        self.doc = self.nlp(phrase)
        self.sentences = list(self.doc.sents)
        self.triplets = []

    def display_tree(self):
        """ Display the dependency tree at localhost:5000 """
        displacy.serve(self.doc, style='dep', page=True)

    def process(self):
        """ Extract all triplets from given phrase """
        extractor = TripletExtractor(0)

        for sentence in self.sentences:
            print("Sentence: ", sentence)
            print("ROOT: ", sentence.root)

            question_triplets = extractor.process(sentence, "q")
            print(question_triplets)
            self.triplets += question_triplets

        self.triplets = list(set(self.triplets))
        self.triplets.sort()
        print("Question triplets: ", self.triplets)
        return self.triplets
