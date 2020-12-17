import spacy
from spacy.matcher import Matcher
from spacy.matcher import Matcher
from text_extractor import TextExtractor
from merge_classes import NounMerger, VerbMerger, SRLComponent, PrepMerger
import pandas as pd
from span2triples import getDobjfromSpan, getPobjfromSpan, getSubjfromSpan


class TriplesExtractor:

    def __init__(self, text):

        model_path = "../model/bert-base-srl-2020.11.19.tar"
        self.nlp = spacy.load('en_core_web_sm')
        self.nlp.add_pipe(PrepMerger(self.nlp))
        self.nlp.add_pipe(NounMerger(self.nlp), last=True)
        self.nlp.add_pipe(VerbMerger(self.nlp), last=True)
        self.nlp.add_pipe(SRLComponent(model_path), last=True)
        self.doc = self.nlp(text)


    def getTriples(self):        
        matcher = Matcher(self.nlp.vocab)
        pattern = [{"LEMMA": "be"}, 
                {"TAG": "VBN"},]
        matcher.add("PASSIVE", None, pattern)  # add pattern

        matches = matcher(self.doc)
        for match_id, start, end in matches:
            span = self.doc[start:end]
            verb = span[-1]
            print(verb)
            print(verb._.srl_arg0)
            print(verb._.srl_arg1)
            print(verb._.srl_arg2)
            print(verb._.srl_argm)



            print(verb._.srl_arg1.root) 
            print(getSubjfromSpan(arg1))
            if verb._.srl_arg2 != None:
                print(getPobjfromSpan(self.nlp, verb._.srl_arg2, verb))
            print('________')

   