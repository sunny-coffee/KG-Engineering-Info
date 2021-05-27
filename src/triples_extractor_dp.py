import spacy
from spacy.matcher import Matcher
from text_extractor import TextExtractor
from custom_components import NounMerger, VerbMerger, SRLComponent, PrepMerger, DashMerger, BetweenMerger, VerbPhraseMerger, LongestVerbMerger
import pandas as pd
from span2triples import getNounPhrasefromSpan, getPobjfromSpan, getInffromSpan


class DP2TriplesExtractor:

    def __init__(self, text):

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
        self.doc = nlp(text)
        # for tok in self.doc:
        #     print(tok,tok._.key, tok._.srl_arg0)
        self.prepObjMatcher = Matcher(nlp.vocab)
        pattern = [{"DEP": "prep"},
                    {"POS": "DET", "OP":"*"},
                    {"POS": "NOUN"}]
        self.prepObjMatcher.add("pobj", None, pattern)
        self.infMatcher = Matcher(nlp.vocab)
        pattern1 = [{"DEP": "prep"},
                    {"TAG": "VB", "DEP":"acl"}]
        pattern2 = [{"DEP": "aux", "POS": "PART"},
                    {"TAG": "VB", "DEP":"advcl"}]
        self.infMatcher.add("infinitive", None, pattern1)
        self.infMatcher.add("infinitive", None, pattern2)


    def getSpan(self, tok, clauseList):
        indexList = list(t.i for t in clauseList if t in tok.subtree)
        subjIndex = tok.i
        minIndex = subjIndex
        maxIndex = subjIndex
        while True:
            exsitNewIndex = False
            for i in indexList:
                if i == minIndex - 1:
                    minIndex = i
                    exsitNewIndex = True
                elif i == maxIndex + 1:
                    maxIndex = i
                    exsitNewIndex = True
            if not exsitNewIndex:
                break
        if minIndex < maxIndex:
            return self.doc[minIndex: maxIndex+1]
        else:
            return self.doc[minIndex]
 
    def getTriples(self): 
        triples = []
        restrictions = []
        inhers = []
        # for tok in self.doc:
        #     print(tok, tok.pos_, tok.tag_, tok.dep_, tok.head)
        # for sent in self.doc.sents:
        #     subjList = list(t for t in sent if 'subj' in t.dep_)
        for tok in self.doc:
            if tok.dep_ == 'ROOT' and tok.pos_ == 'VERB' :
                subject = list(t for t in tok.children if 'subj' in t.dep_)
                if len(subject):
                    dictList = []
                    dictList.append({"verb": [tok], "subj": subject[0], "clause": list(t for t in tok.subtree)} )

                    for tok3 in tok.subtree:
                        # print(tok3, tok3.dep_,tok3.head)
                        if tok3.dep_ == 'conj' and tok3.head == tok and tok3.pos_ == 'VERB':

                            if abs(tok3.i - tok.i) <= 2:
                                for li in dictList:
                                    if tok in li['verb']:
                                        li['verb'].append(tok3)
                                        li['clause'].remove(tok3)
                                        li['clause'].remove(self.doc[tok3.i-1])
                            else:
                                dictList.append({"verb": [tok3], "subj": subject[0], "clause": list(t for t in tok3.subtree)} )
                                for li in dictList:
                                    if tok in li['verb']:
                                        li['clause'] = list(t for t in li['clause'] if t not in tok3.subtree)
                                        # li['clause'].remove(tok3)
                                        li['clause'].remove(self.doc[tok3.i-1])

                    # subjList = list(t for t in tok.children if 'subj' in t.dep_)
                    for tok2 in dictList[0]['clause']:
                        # subj = list(t for t in tok.children if 'subj' in t.dep_)
                        if 'subj' in tok2.dep_ and tok2.head not in list(j for i in dictList for j in i['verb']):
                            verb = tok2.head
                            # if verb.dep_ == 'relcl' or verb.dep_ == 'rcmod':
                            #     dictList.append({"verb": [verb], "subj": verb.head, "clause": list(t for t in verb.subtree)} )
                            # else:
                            dictList.append({"verb": [verb], "subj": tok2, "clause": list(t for t in verb.subtree)} )
                            dictList[0]['clause'] = list(t for t in dictList[0]['clause'] if t not in verb.subtree)
                            for tok3 in verb.subtree:
                                # print(tok3, tok3.dep_,tok3.head)
                                if tok3.dep_ == 'conj' and tok3.head == verb and tok3.pos_ == 'VERB':
                                    
                                    if abs(tok3.i - verb.i) <= 2:
                                        for li in dictList:
                                            if verb in li['verb']:
                                                li['verb'].append(tok3)
                                                li['clause'].remove(tok3)
                                                li['clause'].remove(self.doc[tok3.i-1])
                                    else:
                                        for li in dictList:
                                            if verb in li['verb']:
                                                li['clause'] = list(t for t in li['clause'] if t not in tok3.subtree)
                                                li['clause'].remove(tok3)
                                                li['clause'].remove(self.doc[tok3.i-1])
                                                dictList.append({"verb": [tok3], "subj": li['subj'], "clause": list(t for t in tok3.subtree)} )
                            
                    for dict in dictList:      
                        

                        # indexList = list(t.i for t in dict['clause'] if t in dict['subj'].subtree)
                        print(self.getSpan(dict['subj'], dict['clause']))
                        for verb in dict['verb']:
                            for tok in dict['clause']:

                                if tok.dep_ == 'dobj' and tok.head == verb:
                                    print(self.getSpan(tok, dict['clause']))

                                if tok.dep_ == 'prep' and tok.head == verb:
                                    print('prep')
                                    print(self.getSpan(tok, dict['clause']))

                                if tok.dep_ == 'advcl' and tok.head == verb:
                                    print('to')
                                    print(self.getSpan(tok, dict['clause']))  
                                    infinitive = self.getSpan(tok, dict['clause'])
                                    print(getInffromSpan(self.infMatcher,self.prepObjMatcher,infinitive, verb))
                        # subjSpan = self.doc[minIndex:maxIndex]
                        # print(subjSpan.text)
                        # subSpanList = 
        #         subjList = []
        #         subjPhrases = getNounPhrasefromSpan(self.prepObjMatcher,subjSpan,verb,'subj')
        #         # print(subjSpan)
        #         # print(subjPhrases)
        #         if not subjPhrases:
        #             continue
        #         else:                      
        #             [subjList, sub_restrictions, sub_inhers] = subjPhrases
        #             restrictions.extend(sub_restrictions)
        #             inhers.extend(sub_inhers)
        #         # print(subjList)
        #         # print('!!!!!!!!!!!!!!!!!!!!!!')
        #         #生成直接宾语列表
        #         dobjList = []
        #         if dobjSpan != None:
        #             dobjPhrases = getNounPhrasefromSpan(self.prepObjMatcher, dobjSpan, verb, 'dobj')
        #             if dobjPhrases != False:                     
        #                 [dobjList, sub_restrictions, sub_inhers] = dobjPhrases
        #                 restrictions.extend(sub_restrictions)
        #                 inhers.extend(sub_inhers)
        #         #生成介宾状语
        #         pobjList = []
        #         if verb._.srl_arg2 != None:
        #             arg2_dep = verb._.srl_arg2.root.dep_
        #             # print(verb._.srl_arg2.root)
        #             # print("!!!!!!!!!!!!!!!")
        #             if arg2_dep == 'prep':
        #                 [pobjList, sub_restrictions,sub_inhers] = getPobjfromSpan(self.prepObjMatcher,verb._.srl_arg2, verb)
        #             # print(pobjList)
        #                 restrictions.extend(sub_restrictions)
        #                 inhers.extend(sub_inhers)
        #             elif arg2_dep == 'dative':
        #                 continue
        #             else:
        #                 pass
        #         # if len(pobjList):
        #         #     for subj in subjList:
        #         #         for pobj in pobjList:
        #         #             triples.append({"subject":subj ,"relation": verb.text + ' ' + pobj[0], "object": pobj[1]})

        #         #生成不定式
        #         if len(verb._.srl_argm):
        #             for argm in verb._.srl_argm:
        #                 [infList, sub_restrictions,sub_inhers] = getInffromSpan(self.infMatcher,self.prepObjMatcher,argm, verb)
        #                 restrictions.extend(sub_restrictions)
        #                 inhers.extend(sub_inhers)
        #                 for subj in subjList:
        #                     for inf in infList:
        #                         triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + inf[0], "object": inf[1]})
                               
        #                 [sub_pobjList, sub_restrictions2, sub_inhers2] = getPobjfromSpan(self.prepObjMatcher,argm, verb)
        #                 restrictions.extend(sub_restrictions2)
        #                 inhers.extend(sub_inhers2)
        #                 pobjList.extend(sub_pobjList)

        #         if len(dobjList):
        #             for subj in subjList:
        #                 for dobj in dobjList:
        #                     triples.append({"subject":subj ,"relation": verb.lemma_ , "object": dobj})
        #                     for pobj in pobjList:
        #                         triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + dobj + ' ' + pobj[0], "object": pobj[1]})
        #         else: 
        #             if len(pobjList):
        #                 for subj in subjList:
        #                     for pobj in pobjList:
        #                         triples.append({"subject":subj ,"relation": verb.lemma_ + ' ' + pobj[0], "object": pobj[1]}) 


        # df_triple = pd.DataFrame(triples)
        # df_restriction = pd.DataFrame(restrictions)
        # df_inherit = pd.DataFrame(inhers)
        # pd.set_option('display.max_rows', None)
        # return [df_restriction, df_triple, df_inherit] 


        # for tok in self.doc:
        #     # print(tok, tok.dep_, tok.pos_, tok.head)
        #     if tok.dep_ == 'ROOT' and tok.pos_ == 'VERB' :
        #         print(tok)
        #         dictList = []
        #         dictList.append({"verb": tok, "clause": list(t for t in tok.subtree)} )
        #         while True:
        #             exsitNewVerb = False

        #             # print(list(t.text for t in dictList[0]['clause']))
        #             for tok2 in dictList[0]['clause']:
        #                 # print('!!')
        #                 # print(list(t.text for t in dictList[0]['clause']))
        #                 if tok2 not in list(i['verb'] for i in dictList) and tok2.head in list(i['verb'] for i in dictList) and (tok2.dep_ == 'conj' or tok2.dep_ == 'relcl') and tok2.pos_ == 'VERB':
        #                     print('!!!')
        #                     dictList.append({"verb": tok2, "clause": tok2.subtree} )
        #                     dictList[0]['clause'] = list(t for t in dictList[0]['clause'] if t not in tok2.subtree)
        #                     exsitNewVerb = True

        #             # print(list(t.text for t in dictList[0]['clause']))

        #             if not exsitNewVerb:
        #                 break
                    

        #         for li in dictList:      
        #             print(li['verb'], list(t.text for t in li['clause']))
        #         dobjSpan = None
        #         if verb._.srl_arg0 != None:
        #             subjSpan = verb._.srl_arg0
        #             if verb._.srl_arg1 != None:
        #                 dobjSpan= verb._.srl_arg1
        #         else:
        #             if verb._.srl_arg1 != None:
        #                 subjSpan= verb._.srl_arg1
        #             else:
        #                 continue
        #         #生成主语列表   