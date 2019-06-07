from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from pprint import pprint
from rdflib import Graph, Literal, URIRef
from rdflib import Namespace


from sentence_processor import SentenceProcessor
from question_processor import QuestionProcessor


class Conversation:

    def __init__(self, file="agent.rdf"):
        self.end_sentences = ["exit", "enough for now", "goodbye", "goodnight",
                              "bye", "that is all", "that's all for now"]
        self.greetings = ["hi", "hello", "hi there", "hello there",
                          "good morning", "good afternoon", "hey"]
        self.rdf_file = file
        self.g = Graph()
        self.n = Namespace("http://agent.org/")
        self.g.serialize(self.rdf_file)
        self.stemmer = PorterStemmer()
        self.lemm = WordNetLemmatizer()
        self.no = 1
        self.wh_list = ["who", "what", "where", "why", "when", "which", "how"]

    def listen(self, phrase):
        """ Construct and update the RDF Graph based on triplets extracted
            during a conversation
        """
        sentence_processor = SentenceProcessor(phrase, self.no)
        self.no += 1
        triplets = sentence_processor.process()
        g = Graph()
        n = self.n
        g.parse(self.rdf_file, format="xml")

        for triplet in triplets:
            s, p, o = triplet
            # s, p, o = self.stemmer.stem(s), self.stemmer.stem(p), self.stemmer.stem(o)
            s, p, o = self.lemm.lemmatize(s), self.lemm.lemmatize(p), self.lemm.lemmatize(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            print(s, p, o)
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)

            g.add((subj, pred, obj))

        g.serialize(self.rdf_file)

    def yes_no_query(self, triplets, g):
        query_triplets = []
        n = self.n
        for triplet in triplets:
            s, p, o = triplet
            # s, p, o = self.stemmer.stem(s), self.stemmer.stem(p), self.stemmer.stem(o)
            s, p, o = self.lemm.lemmatize(s), self.lemm.lemmatize(p), self.lemm.lemmatize(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            print(s, p, o)
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)
            query_triplets.append((subj, pred, obj))

        if all([True if triplet in g else False
                for triplet in query_triplets
                ]):
            response = "Yes."
        else:
            response = "No."
        return response

    def wh_query(self, triplets, g):
        query_properties = {}
        query_responses = []
        n = self.n
        for triplet in triplets:
            s, p, o = triplet
            if any([s == "what", o == "what"]):
                continue
            # s, p, o = self.stemmer.stem(s), self.stemmer.stem(p), self.stemmer.stem(o)
            s, p, o = self.lemm.lemmatize(s), self.lemm.lemmatize(p), self.lemm.lemmatize(o)
            s, p, o = s.replace(" ", "_"), p.replace(" ", "_"), o.replace(" ", "_")
            print(s, p, o)
            subj, pred, obj = URIRef(n + s), URIRef(n + p), URIRef(n + o)

            q = """PREFIX agent: <http://agent.org/>
            SELECT ?o
            WHERE {{
                agent:{} agent:{} ?o.
            }}""".format(s, p)
            print(q)
            query_responses.append(g.query(q))

        print(query_responses)

        string_responses = []
        for response in query_responses:
            for element in response:
                for triplet in element:
                    word = triplet.split("/")[-1]
                    if word == "null":
                        continue
                    string_responses.append(word)
                    query_properties[word] = []

        print(string_responses)
        for word in string_responses:
            q_p = """PREFIX agent: <http://agent.org/>
            SELECT ?p ?o
            WHERE {{
                agent:{} ?p ?o.
            }}""".format(word)
            print(q_p)
            query_properties[word].append(g.query(q_p))

        complex_responses = ""
        object_type = None
        for key in query_properties:
            element_properties = ""
            for result in query_properties[key]:
                for element in result:
                    print(element)
                    properties = ""
                    if element[-2].split("/")[-1] == "is_a":
                        object_type = element[-1].split("/")[-1]
                        continue

                    property = element[-1].split("/")[-1]

                    if property == "null":
                        continue
                    print(property)
                    element_properties += property + " "
            complex_responses += element_properties + object_type

        return complex_responses


    def reply(self, phrase):
        """ Construct query and interogate RDF Graph based on triplets extracted
            during a conversation
        """
        g = Graph()
        g.parse(self.rdf_file, format="xml")

        response = ""

        question_processor = QuestionProcessor(phrase)
        triplets = question_processor.process()
        wh_list = self.wh_list
        # TODO: costruct queries

        # yes/no questions
        if phrase.split()[0].lower() not in wh_list:
            response = self.yes_no_query(triplets, g)
        else:
            response = self.wh_query(triplets, g)

        # return response

        return response

    def process(self, phrase):
        bot_reply = ""
        if phrase.lower().strip("!").strip(".") in self.end_sentences:
            bot_reply = "Glad we talked!"
        elif phrase.lower().strip("!").strip(".") in self.greetings:
            bot_reply = "Hello! What a wonderful day!"
        elif ('?' in phrase)  or (phrase.split()[0] in self.wh_list):
            bot_reply = self.reply(phrase + "?")
        else:
            self.listen(phrase)
            bot_reply = "Roger that!"

        return bot_reply
