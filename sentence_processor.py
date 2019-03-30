import itertools
import re
import spacy
from spacy import displacy
from pprint import pprint

from triplet_extractor import TripletExtractor


class SentenceProcessor:

    def __init__(self, phrase):
        self.nlp = spacy.load('en')
        self.doc = self.nlp(phrase)
        self.sentences = list(self.doc.sents)
        self.triplets = []

    def find_split_marker_advcl(self, document):
        markers = []
        for item in list(document):
            if item.dep_ == "mark":
                markers.append(item.text)
        return markers

    def create_delimiters(self, markers_list):
        delimiters = ''
        for delimiter in markers_list:
            delimiters += delimiter + '|'
        return delimiters[:-1]

    def display_tree(self):
        displacy.serve(self.doc, style='dep', page=True)

    def process(self):
        extractor = TripletExtractor()

        for sentence in self.sentences:
            print("Sentence: ", sentence)
            print("ROOT: ", sentence.root)

            clauses = [sentence]
            if "advcl" in [elem.dep_ for elem in list(self.doc)]:
                split_markers = self.find_split_marker_advcl(self.doc)

                clauses = re.split(self.create_delimiters(split_markers), sentence.text)
                clauses = [self.nlp(c) for c in clauses]

            for clause in clauses:
                print("Clause: ", clause)
                if type(clause) == type(self.nlp(" ")):
                    clause = list(clause.sents)[0]

                clause_triplets = extractor.process(clause)

                print(clause_triplets)
                self.triplets += clause_triplets
        return list(set(self.triplets))
