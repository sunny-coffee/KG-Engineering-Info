import spacy
from spacy.matcher import Matcher
from spacy.matcher import Matcher
from text_extractor import TextExtractor
from merge_classes import NounMerger, VerbMerger, SRLComponent, PrepMerger
import pandas as pd
from span2triples import getDobjfromSpan, getPobjfromSpan, getSubjfromSpan, getInffromSpan


class TriplesExtractor:

    def __init__(self, text):

        model_path = "../model/bert-base-srl-2020.11.19.tar"
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe(PrepMerger(nlp))
        nlp.add_pipe(NounMerger(nlp))
        nlp.add_pipe(VerbMerger(nlp))
        nlp.add_pipe(SRLComponent(model_path), last=True)
        self.doc = nlp(text)
        # for tok in self.doc:
        #     print(tok,tok.dep_,tok.pos_,tok.tag_,tok.head,tok._.srl_argm)
        self.prepObjMatcher = Matcher(nlp.vocab)
        pattern = [{"DEP": "prep"},
                    {"POS": "DET", "OP":"*"},
                    {"POS": "NOUN"}]
        self.prepObjMatcher.add("pobj", None, pattern)
        self.infMatcher = Matcher(nlp.vocab)
        pattern = [{"DEP": "prep"},
                    {"TAG": "VB", "DEP":"acl"}]
        self.infMatcher.add("infinitive", None, pattern)

    def getPassiveTriples(self): 
        triples = []
        for tok in self.doc:
            if tok.tag_ == 'VBN':
                verb = tok    
                subjList = []
                # print(verb._.srl_arg1)
                if verb._.srl_arg1 != None:
                    subjList = getSubjfromSpan(self.prepObjMatcher,verb._.srl_arg1)
                # print(subjList)
                if not len(subjList):            
                    continue
                pobjList = []
                # print(verb._.srl_arg2)
                if verb._.srl_arg2 != None:
                    pobjList = getPobjfromSpan(self.prepObjMatcher,verb._.srl_arg2, verb)
                # print(pobjList)
                if len(pobjList):
                    for subj in subjList:
                        for pobj in pobjList:
                            triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})

                if len(verb._.srl_argm):
                    for argm in verb._.srl_argm:
                        infList = getInffromSpan(self.infMatcher,argm, verb)
                        # print(infList)
                        for subj in subjList:
                            for inf in infList:
                                triples.append({"subject":subj ,"relation": verb.text + ' ' + inf[0], "object": inf[1]})

            # if tok.tag_ == 'VBD' or tok.tag_ == 'VBZ' or tok.tag_ == 'VBP' or tok.tag_ == 'VBG':
            #     verb = tok



        df = pd.DataFrame(triples)
        return df    

   