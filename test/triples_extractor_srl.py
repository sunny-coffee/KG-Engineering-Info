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
        self.triples = []
        self.restrictions = []
        self.inhers = []

    def getTriples(self):
        for sent in self.doc.sents:
            print(sent.text)
            for tok in sent:
                # print(tok.text, tok.lemma_, tok.pos_, tok.tag_)
                if tok.tag_ == 'VBN':
                    self.getPassiveTriples(tok)
                if (tok.tag_ == 'VBD' or tok.tag_ == 'VBG' or tok.tag_ == 'VBP' or tok.tag_ == 'VBZ' or tok.tag_ == 'VB'):
                    if tok.pos_ != 'AUX':
                        # print(tok,'|', tok._.srl_arg0,' |  ',tok._.srl_arg1,'  | ',tok._.srl_arg2,'  | ',tok._.srl_argm)
                        self.getActiveTriples(tok)
                    else:
                        self.getCopulaTriples(tok)
        df_triple = pd.DataFrame(self.triples)
        df_restriction = pd.DataFrame(self.restrictions)
        df_inherit = pd.DataFrame(self.inhers)
        pd.set_option('display.max_rows', None)
        return [df_restriction, df_triple, df_inherit]

    def getPassiveTriples(self, verb): 

        #生成主语列表   
        subjList = []
        # print(verb._.srl_arg1)
        if verb._.srl_arg1 != None:
            nounPhrases = getNounPhrasefromSpan(self.prepObjMatcher,verb._.srl_arg1,verb,'all')
            if not nounPhrases:
                return False
            else:                      
                [subjList, sub_restrictions, sub_inhers] = nounPhrases
                self.restrictions.extend(sub_restrictions)
                self.inhers.extend(sub_inhers)
                
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
                self.restrictions.extend(sub_restrictions)
                self.inhers.extend(sub_inhers)
                # print(infList)
                for subj in subjList:
                    for inf in infList:
                        self.triples.append({"subject":subj ,"relation": verb.text + ' ' + inf[0], "object": inf[1]})
                        print(subj,'|', verb.text + ' ' + inf[0],'|', inf[1])
                        
                [sub_pobjList, sub_restrictions2, sub_inhers2] = getPobjfromSpan(self.prepObjMatcher,argm, verb)
                self.restrictions.extend(sub_restrictions2)
                pobjList.extend(sub_pobjList)
                self.inhers.extend(sub_inhers2)
        if len(pobjList):
            for subj in subjList:
                for pobj in pobjList:
                    self.triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})
                    print(subj ,'|',verb.text + ' ' + pobj[0],'|', pobj[1])

    def getActiveTriples(self, verb): 
        
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
                return False

        #生成主语列表   
        subjList = []
        if not subjPhrases:
            return False
        else:                      
            [subjList, sub_restrictions, sub_inhers] = subjPhrases
            # print(subjList)
            self.restrictions.extend(sub_restrictions)
            self.inhers.extend(sub_inhers)
        

        dobjList = []
        if dobjSpan != None:
            dobjPhrases = getNounPhrasefromSpan(self.prepObjMatcher, dobjSpan, verb, 'all')
            if dobjPhrases != False:                     
                [dobjList, sub_restrictions, sub_inhers] = dobjPhrases
                self.restrictions.extend(sub_restrictions)
                self.inhers.extend(sub_inhers)


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
                self.restrictions.extend(sub_restrictions)
                self.inhers.extend(sub_inhers)
                for subj in subjList:
                    for inf in infList:
                        self.triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + inf[0], "object": inf[1]})
                        print(subj, '|',verb.text + ' ' + inf[0], '|',inf[1])
                [sub_pobjList, sub_restrictions2, sub_inhers2] = getPobjfromSpan(self.prepObjMatcher,argm, verb)
                self.restrictions.extend(sub_restrictions2)
                self.inhers.extend(sub_inhers2)
                pobjList.extend(sub_pobjList)

        if len(dobjList):
            for subj in subjList:
                for dobj in dobjList:
                    self.triples.append({"subject":subj ,"relation": verb.lemma_ , "object": dobj})
                    print(subj ,'|',verb.lemma_ ,'|', dobj)
                    for pobj in pobjList:
                        self.triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + dobj + ' ' + pobj[0], "object": pobj[1]})
                        print(subj ,'|', verb.lemma_ + ' ' + pobj[0], '|',pobj[1]) 
        else: 
            if len(pobjList):
                for subj in subjList:
                    for pobj in pobjList:
                        self.triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + pobj[0], "object": pobj[1]})
                        print(subj ,'|', verb.lemma_ + ' ' + pobj[0],'|', pobj[1])
      


    def getCopulaTriples(self, verb): 
                
        # print(verb._.srl_arg0, '||', verb._.srl_arg1, '||',verb._.srl_arg2, '||',verb._.srl_argm)
        if verb._.srl_arg1 != None:
            subjSpan = verb._.srl_arg1
        else:
            return False
        dobjSpan = verb._.srl_arg2
        #生成主语列表   
        # subjList = [subjSpan.lemma_]
        # print(subjSpan)
        subjList = []
        subjPhrases = getNounPhrasefromSpan(self.prepObjMatcher,subjSpan,verb,'all')
        if not subjPhrases:
            return False
        else:                      
            [subjList, sub_restrictions, sub_inhers] = subjPhrases
            self.restrictions.extend(sub_restrictions)
            self.inhers.extend(sub_inhers)

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
                self.restrictions.extend(sub_restrictions)
                self.inhers.extend(sub_inhers)
            else:
                options.append(verb._.srl_arg2)


        # #生成介宾状语
        pobjList = []
                        
        # print(options)
        if len(options):
            for argm in options:
                [infList, sub_restrictions,sub_inhers] = getInffromSpan(self.infMatcher,self.prepObjMatcher,argm, verb)
                self.restrictions.extend(sub_restrictions)
                self.inhers.extend(sub_inhers)
                for subj in subjList:
                    for inf in infList:
                        self.triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + inf[0], "object": inf[1]})
                        print(subj , '|',verb.lemma_ + ' ' + inf[0], '|',inf[1])
                [sub_pobjList, sub_restrictions2, sub_inhers2] = getPobjfromSpan(self.prepObjMatcher,argm, verb)
                self.restrictions.extend(sub_restrictions2)
                self.inhers.extend(sub_inhers2)
                pobjList.extend(sub_pobjList)
        # print(pobjList)

        if len(dobjList):
            for subj in subjList:
                for dobj in dobjList:
                    self.triples.append({"subject":subj ,"relation": verb.lemma_ , "object": dobj})
                    print(subj ,verb.lemma_ , dobj)
                    for pobj in pobjList:
                        self.triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + dobj + ' ' + pobj[0], "object": pobj[1]})
                        print(subj ,'|',verb.lemma_ + ' ' + dobj + ' ' + pobj[0], '|', pobj[1])
        else: 
            if len(pobjList):
                for subj in subjList:
                    for pobj in pobjList:
                        self.triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + pobj[0], "object": pobj[1]})
                        print(subj,'|',verb.lemma_ + ' ' + pobj[0], '|',pobj[1])
        
       


   