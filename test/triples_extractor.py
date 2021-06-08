import spacy
from spacy.matcher import Matcher
from text_extractor import TextExtractor
from custom_components import NounMerger, VerbMerger, SRLComponent, PrepMerger, DashMerger, BetweenMerger, VerbPhraseMerger, LongestVerbMerger, CopulaMerger
import pandas as pd
from span2triples import getNounPhrasefromSpan, getPobjfromSpan, getInffromSpan


class TriplesExtractor:

    def __init__(self, text):

        model_path = "../model/bert-base-srl-2020.11.19.tar"
        nlp = spacy.load('en_core_web_sm')
        merge_ents = nlp.create_pipe("merge_entities")
        nlp.add_pipe(merge_ents) 
        nlp.add_pipe(PrepMerger(nlp))
        nlp.add_pipe(DashMerger(nlp))
        nlp.add_pipe(BetweenMerger(nlp))
        nlp.add_pipe(NounMerger(nlp))
        nlp.add_pipe(VerbMerger(nlp))
        nlp.add_pipe(VerbPhraseMerger(nlp))
        nlp.add_pipe(LongestVerbMerger(nlp))
        nlp.add_pipe(CopulaMerger(nlp))
        nlp.add_pipe(SRLComponent(model_path), last=True)
        self.doc = nlp(text)
        # for tok in self.doc:
        #     print(tok,tok._.key, tok._.srl_arg0)
        self.prepObjMatcher = Matcher(nlp.vocab)
        pattern = [{"POS": "ADP"},
                    {"POS": "DET", "OP":"*"},
                    {"POS": "NOUN"}]
        self.prepObjMatcher.add("pobj", None, pattern)
        self.infMatcher = Matcher(nlp.vocab)
        pattern1 = [{"DEP": "prep"},
                    {"TAG": "VB", "DEP":"acl"}]
        pattern2 = [{"DEP": "aux", "TAG": "To"},
                    {"TAG": "VB", "DEP":"advcl"}]
        self.infMatcher.add("infinitive", None, pattern1)
        self.infMatcher.add("infinitive", None, pattern2)

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

                #生成不定式
                
                if verb._.srl_argm != None:
                    options = verb._.srl_argm
                else:
                    options = []
                if verb._.srl_arg2 != None:
                    options.append(verb._.srl_arg2)
                if len(options):
                    for argm in options:
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
            if (tok.tag_ == 'VBD' or tok.tag_ == 'VBG' or tok.tag_ == 'VBP' or tok.tag_ == 'VBZ' or tok.tag_ == 'VB') and tok.pos_ != 'AUX':
                verb = tok 
                # print(tok)

                

                dobjSpan = None
                # print(verb._.srl_arg0, verb._.srl_arg1, verb._.srl_argm)
                if verb._.srl_arg0 != None:
                    subjSpan = verb._.srl_arg0
                    subjPhrases = getNounPhrasefromSpan(self.prepObjMatcher,subjSpan,verb,'all')
                    if verb._.srl_arg1 != None:
                        dobjSpan= verb._.srl_arg1
                else:
                    if verb._.srl_arg1 != None:
                        subjSpan= verb._.srl_arg1
                        subjPhrases = getNounPhrasefromSpan(self.prepObjMatcher,subjSpan,verb,'subj')
                        # print(subjSpan)
                    else:
                        continue
    
                #生成主语列表   
                subjList = []
                if not subjPhrases:
                    continue
                else:                      
                    [subjList, sub_restrictions, sub_inhers] = subjPhrases
                    restrictions.extend(sub_restrictions)
                    inhers.extend(sub_inhers)

                dobjList = []
                if dobjSpan != None:
                    dobjPhrases = getNounPhrasefromSpan(self.prepObjMatcher, dobjSpan, verb, 'dobj')
                    if dobjPhrases != False:                     
                        [dobjList, sub_restrictions, sub_inhers] = dobjPhrases
                        restrictions.extend(sub_restrictions)
                        inhers.extend(sub_inhers)


                # #生成介宾状语
                pobjList = []
                if verb._.srl_argm != None:
                    options = verb._.srl_argm
                else:
                    options = []
                if verb._.srl_arg2 != None:
                    options.append(verb._.srl_arg2)
                if len(options):
                    for argm in options:
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


    def getCopulaTriples(self): 
        triples = []
        restrictions = []
        inhers = []
        for tok in self.doc:
            if (tok.tag_ == 'VBD' or tok.tag_ == 'VBG' or tok.tag_ == 'VBP' or tok.tag_ == 'VBZ' or tok.tag_ == 'VB') and tok.pos_ == 'AUX':
                verb = tok 
                
                # print(verb._.srl_arg0, '||', verb._.srl_arg1, '||',verb._.srl_arg2, '||',verb._.srl_argm)
                if verb._.srl_arg1 != None:
                    subjSpan = verb._.srl_arg1
                else:
                    continue
                dobjSpan = verb._.srl_arg2
                #生成主语列表   
                # subjList = [subjSpan.lemma_]
                # print(subjSpan)
                subjList = []
                subjPhrases = getNounPhrasefromSpan(self.prepObjMatcher,subjSpan,verb,'all')
                if not subjPhrases:
                    continue
                else:                      
                    [subjList, sub_restrictions, sub_inhers] = subjPhrases
                    restrictions.extend(sub_restrictions)
                    inhers.extend(sub_inhers)

                if verb._.srl_argm != None:
                    options = verb._.srl_argm
                else:
                    options = []

                dobjList = []
                # print(dobjSpan)
                if dobjSpan != None:
                    dobjPhrases = getNounPhrasefromSpan(self.prepObjMatcher, dobjSpan, verb, 'attr')
                    # print(dobjPhrases)
                    if dobjPhrases != False:                     
                        [dobjList, sub_restrictions, sub_inhers] = dobjPhrases
                        restrictions.extend(sub_restrictions)
                        inhers.extend(sub_inhers)
                    else:
                        options.append(verb._.srl_arg2)


                # #生成介宾状语
                pobjList = []
                             
                # print(options)
                if len(options):
                    for argm in options:
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
                # print(pobjList)

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


   