import spacy
from spacy.matcher import Matcher
from spacy.matcher import Matcher
from text_extractor import TextExtractor
from merge_classes import NounMerger, VerbMerger, SRLComponent, PrepMerger
import pandas as pd
from span2triples import getNounPhrasefromSpan, getPobjfromSpan, getInffromSpan


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

    # def getPassiveTriples(self): 
    #     triples = []
    #     for tok in self.doc:
    #         if tok.tag_ == 'VBN':
    #             verb = tok 
    #             #生成主语列表   
    #             subjList = []
    #             # print(verb._.srl_arg1)
    #             if verb._.srl_arg1 != None:
    #                 nounPhrases = getNounPhrasefromSpan(self.prepObjMatcher,verb._.srl_arg1,verb,'subj')
    #                 if not nounPhrases:
    #                     continue
    #                 else:                      
    #                     [subjList, sub_triples] = nounPhrases
    #                     triples.extend(sub_triples)
                        
    #             #生成介宾状语
    #             pobjList = []
    #             # print(verb._.srl_arg2)
    #             if verb._.srl_arg2 != None:
    #                 [pobjList, sub_triples] = getPobjfromSpan(self.prepObjMatcher,verb._.srl_arg2, verb)
    #             # print(pobjList)
    #                 triples.extend(sub_triples)
    #             # if len(pobjList):
    #             #     for subj in subjList:
    #             #         for pobj in pobjList:
    #             #             triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})

    #             #生成不定式
    #             if len(verb._.srl_argm):
    #                 for argm in verb._.srl_argm:
    #                     [infList, sub_triples] = getInffromSpan(self.infMatcher,self.prepObjMatcher,argm, verb)
    #                     triples.extend(sub_triples)
    #                     # print(infList)
    #                     for subj in subjList:
    #                         for inf in infList:
    #                             triples.append({"subject":subj ,"relation": verb.text + ' ' + inf[0], "object": inf[1]})
                               
    #                     [sub_pobjList, sub_triples2] = getPobjfromSpan(self.prepObjMatcher,argm, verb)
    #                     triples.extend(sub_triples2)
    #                     pobjList.extend(sub_pobjList)
    #             if len(pobjList):
    #                 for subj in subjList:
    #                     for pobj in pobjList:
    #                         triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})

    def getActiveTriples(self): 
        triples = []
        for tok in self.doc:
            if tok.tag_ == 'VBD' or tok.tag_ == 'VBN' or tok.tag_ == 'VBP' or tok.tag_ == 'VBZ':
                verb = tok 

                if verb._.srl_arg0 != None:
                    subjSpan = verb._srl_arg0
                elif verb._.srl_arg1 != None:
                    subjSpan = verb._srl_arg1
                else:
                    continue

                #生成主语列表   
                subjList = []
                nounPhrases = getNounPhrasefromSpan(self.prepObjMatcher,verb._.srl_arg1,verb,'subj')
                if not nounPhrases:
                    continue
                else:                      
                    [subjList, sub_triples] = nounPhrases
                    triples.extend(sub_triples)
                
                        
                #生成介宾状语
                pobjList = []
                # print(verb._.srl_arg2)
                if verb._.srl_arg2 != None:
                    arg2_dep = verb._.srl_arg2.root.dep_
                    if arg2_dep == 'prep':
                        [pobjList, sub_triples] = getPobjfromSpan(self.prepObjMatcher,verb._.srl_arg2, verb)
                    # print(pobjList)
                        triples.extend(sub_triples)
                    elif arg2_dep == 'dative':
                        continue
                    else:
                        pass
                # if len(pobjList):
                #     for subj in subjList:
                #         for pobj in pobjList:
                #             triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})

                #生成不定式
                if len(verb._.srl_argm):
                    for argm in verb._.srl_argm:
                        [infList, sub_triples] = getInffromSpan(self.infMatcher,self.prepObjMatcher,argm, verb)
                        triples.extend(sub_triples)
                        # print(infList)
                        for subj in subjList:
                            for inf in infList:
                                triples.append({"subject":subj ,"relation": verb.text + ' ' + inf[0], "object": inf[1]})
                               
                        [sub_pobjList, sub_triples2] = getPobjfromSpan(self.prepObjMatcher,argm, verb)
                        triples.extend(sub_triples2)
                        pobjList.extend(sub_pobjList)
                if len(pobjList):
                    for subj in subjList:
                        for pobj in pobjList:
                            triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})




        df = pd.DataFrame(triples)
        pd.set_option('display.max_rows', None)
        return df    

   