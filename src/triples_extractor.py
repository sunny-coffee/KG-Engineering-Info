import spacy
from spacy.matcher import Matcher
from spacy.matcher import Matcher
from text_extractor import TextExtractor
from merge_classes import NounMerger, VerbMerger, SRLComponent, PrepMerger, DashMerger , BetweenMerger
import pandas as pd
from span2triples import getNounPhrasefromSpan, getPobjfromSpan, getInffromSpan


class TriplesExtractor:

    def __init__(self, text):

        model_path = "../model/bert-base-srl-2020.11.19.tar"
        nlp = spacy.load('en_core_web_sm')
        merge_ents = nlp.create_pipe("merge_entities")
        nlp.add_pipe(merge_ents)
        nlp.add_pipe(NounMerger(nlp)) 
        # nlp.add_pipe(PrepMerger(nlp))
        nlp.add_pipe(DashMerger(nlp))
        # nlp.add_pipe(BetweenMerger(nlp))
        # nlp.add_pipe(VerbMerger(nlp))
        nlp.add_pipe(SRLComponent(model_path), last=True)
        self.doc = nlp(text)
        for tok in self.doc:
            print(tok,tok._.key, tok.lemma_)
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
        restrictions = []
        inhers = []
        for tok in self.doc:
            if tok.tag_ == 'VBN':
                verb = tok 
                #生成主语列表   
                subjList = []
                # print(verb._.srl_arg1)
                if verb._.srl_arg1 != None:
                    nounPhrases = getNounPhrasefromSpan(self.prepObjMatcher,verb._.srl_arg1,verb,'subj')
                    if not nounPhrases:
                        continue
                    else:                      
                        [subjList, sub_restrictions, sub_inhers] = nounPhrases
                        restrictions.extend(sub_restrictions)
                        inhers.extend(sub_inhers)
                        
                #生成介宾状语
                pobjList = []
                # print(verb._.srl_arg2)
                if verb._.srl_arg2 != None:
                    [pobjList, sub_restrictions, sub_inhers] = getPobjfromSpan(self.prepObjMatcher,verb._.srl_arg2, verb)
                # print(pobjList)
                    restrictions.extend(sub_restrictions)
                    inhers.extend(sub_inhers)
                # if len(pobjList):
                #     for subj in subjList:
                #         for pobj in pobjList:
                #             triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})

                #生成不定式
                if len(verb._.srl_argm):
                    for argm in verb._.srl_argm:
                        [infList, sub_restrictions, sub_inhers] = getInffromSpan(self.infMatcher,self.prepObjMatcher,argm, verb)
                        restrictions.extend(sub_restrictions)
                        inhers.extend(sub_inhers)
                        # print(infList)
                        for subj in subjList:
                            for inf in infList:
                                triples.append({"subject":subj ,"relation": verb.text + ' ' + inf[0], "object": inf[1]})
                               
                        [sub_pobjList, sub_restrictions2, sub_inhers2] = getPobjfromSpan(self.prepObjMatcher,argm, verb)
                        restrictions.extend(sub_restrictions2)
                        pobjList.extend(sub_pobjList)
                        inhers.extend(sub_inhers2)
                if len(pobjList):
                    for subj in subjList:
                        for pobj in pobjList:
                            triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})
        
        df_triple = pd.DataFrame(triples)
        df_restriction = pd.DataFrame(restrictions)
        df_inherit = pd.DataFrame(inhers)
        pd.set_option('display.max_rows', None)
        return [df_restriction, df_triple, df_inherit]

    def getActiveTriples(self): 
        triples = []
        restrictions = []
        inhers = []
        for tok in self.doc:
            if tok.tag_ == 'VBD' or tok.tag_ == 'VBG' or tok.tag_ == 'VBP' or tok.tag_ == 'VBZ' or tok.tag_ == 'VB':
                verb = tok 

                dobjSpan = None
                if verb._.srl_arg0 != None:
                    subjSpan = verb._.srl_arg0
                    if verb._.srl_arg1 != None:
                        dobjSpan= verb._.srl_arg1
                else:
                    if verb._.srl_arg1 != None:
                        subjSpan= verb._.srl_arg1
                    else:
                        continue

                #生成主语列表   
                subjList = []
                subjPhrases = getNounPhrasefromSpan(self.prepObjMatcher,subjSpan,verb,'subj')
                if not subjPhrases:
                    continue
                else:                      
                    [subjList, sub_restrictions, sub_inhers] = subjPhrases
                    restrictions.extend(sub_restrictions)
                    inhers.extend(sub_inhers)
                #生成直接宾语列表
                dobjList = []
                if dobjSpan != None:
                    dobjPhrases = getNounPhrasefromSpan(self.prepObjMatcher, dobjSpan, verb, 'dobj')
                    if dobjPhrases != False:                     
                        [dobjList, sub_restrictions, sub_inhers] = dobjPhrases
                        restrictions.extend(sub_restrictions)
                        inhers.extend(sub_inhers)
                #生成介宾状语
                pobjList = []
                if verb._.srl_arg2 != None:
                    arg2_dep = verb._.srl_arg2.root.dep_
                    # print(verb._.srl_arg2.root)
                    # print("!!!!!!!!!!!!!!!")
                    if arg2_dep == 'prep':
                        [pobjList, sub_restrictions,sub_inhers] = getPobjfromSpan(self.prepObjMatcher,verb._.srl_arg2, verb)
                    # print(pobjList)
                        restrictions.extend(sub_restrictions)
                        inhers.extend(sub_inhers)
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
                        [infList, sub_restrictions,sub_inhers] = getInffromSpan(self.infMatcher,self.prepObjMatcher,argm, verb)
                        restrictions.extend(sub_restrictions)
                        inhers.extend(sub_inhers)
                        for subj in subjList:
                            for inf in infList:
                                triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + inf[0], "object": inf[1]})
                               
                        [sub_pobjList, sub_restrictions2, sub_inhers2] = getPobjfromSpan(self.prepObjMatcher,argm, verb)
                        restrictions.extend(sub_restrictions2)
                        inhers.extend(sub_inhers2)
                        pobjList.extend(sub_pobjList)

                if len(dobjList):
                    for subj in subjList:
                        for dobj in dobjList:
                            triples.append({"subject":subj ,"relation": verb.lemma_ , "object": dobj})
                            for pobj in pobjList:
                                triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + dobj + ' ' + pobj[0], "object": pobj[1]})
                else: 
                    if len(pobjList):
                        for subj in subjList:
                            for pobj in pobjList:
                                triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + pobj[0], "object": pobj[1]})
        
        df_triple = pd.DataFrame(triples)
        df_restriction = pd.DataFrame(restrictions)
        df_inherit = pd.DataFrame(inhers)
        pd.set_option('display.max_rows', None)
        return [df_restriction, df_triple, df_inherit] 

   