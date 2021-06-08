from types import TracebackType
from pandas.core.indexes import category
from spacy.errors import Errors
from spacy.tokens import Token

"""
In this file, some functions are define to detect some certain useful pieces from the input span.
"""

## Detect the noun phrases from the input span
 
def getNounPhrasefromSpan(prepObjMatcher,span,verb,vtype):
    if type(span) == Token:
        if (vtype in span.dep_ or vtype == 'all') and (span.pos_ == 'NOUN' or span.tag_ == 'NNP'):
            return [[span],[],[]]
        else:
            return False
    else:
        root_noun = span.root
    nounList = []
    prepObjList = []
    nounPrepNounList = [] 
    inhers = []  
    if (vtype in root_noun.dep_ or vtype == 'all') and (root_noun.pos_ == 'NOUN' or root_noun.tag_ == 'NNP'):
        matches = prepObjMatcher(span)
        seq = ''
        for match_id, start, end in matches:
            match_span = span[start:end] 
            match_prep = match_span[0]
            if match_prep.head == root_noun:
                prepObjList.append([match_span[0].text, match_span[-1].text])
                seq = seq + ' ' + match_span.text
                if match_span[-1]._.key != None:
                    if (len(match_span[-1].text) - len(match_span[-1]._.key)) > 2:
                        inhers.append({"subclass": match_span[-1].text,"superclass": match_span[-1]._.key})       
        nounPrepNounList.append((root_noun.text  + seq).strip())
        nounList.append(root_noun.text)
        key_noun = root_noun
        try:
            nn = len(key_noun.text) - len(key_noun._.key)
        except BaseException:
            return False
        else: 
            if nn>=2:
                inhers.append({"subclass": key_noun.text,"superclass": key_noun._.key})
        if  ('and' in [tok.text for tok in span]) or ('or' in [tok.text for tok in span]):
            for tok in span:
                if tok.head == key_noun and tok.pos_ == "NOUN" and tok.dep_ == "conj":               
                    nounList.append(tok.text)
                    nounPrepNounList.append((tok.text + seq).strip())
                    key_noun = tok
                    if key_noun._.key != None:
                        if (len(key_noun.text) - len(key_noun._.key))>2:
                            inhers.append({"subclass": key_noun.text,"superclass": key_noun._.key})
    if not len(nounList):            
        return False
    restrictions =[]
    if len(prepObjList):
        for i, npn in enumerate(nounPrepNounList):
            restrictions.append({"subclass":npn ,"superclass": nounList[i], "relation":prepObjList})
    return [nounPrepNounList,  restrictions, inhers]



## Detect the preposition-object phrases from the input span

def getPobjfromSpan(prepObjMatcher,span,verb):
    pobjList = []
    inhers = []
    restrictions = []
    matches1 = prepObjMatcher(span)
    for match_id, start, end in matches1:
        match_span1 = span[start:end] 
        prep = match_span1[0]
        prepObj = match_span1[-1]
        if prepObj._.key != None:
            if (len(prepObj.text) - len(prepObj._.key)) > 2:
                inhers.append({"subclass": prepObj.text,"superclass": prepObj._.key})
        if prep.head == verb:
            prepObjList = []
            matches2 = prepObjMatcher(span)
            seq = ''
            for match_id, start, end in matches2:
                match_span = span[start:end] 
                if match_span[0].head == prepObj:   
                    prepObjList.append([match_span[0].text, match_span[-1].text])
                    seq = seq + ' ' + match_span.text
                    if match_span[-1]._.key != None:
                        if (len(match_span[-1].text) - len(match_span[-1]._.key)) > 2:
                            inhers.append({"subclass": match_span[-1].text,"superclass": match_span[-1]._.key})
            nounPrepNoun = (prepObj.text  + seq).strip()
            pobjList.append([prep.text, nounPrepNoun])
            if len(prepObjList):
                restrictions.append({"subclass":nounPrepNoun , "superclass": prepObj.text, "relation":prepObjList})
    return [pobjList, restrictions, inhers]



## Detect the infinitive from the input span

def getInffromSpan(infMatcher,prepObjMatcher,span,verb):
    infList = []
    restrictions = []
    inhers = []
    matches = infMatcher(span)
    for match_id, start, end in matches:
        match_span = span[start:end] 
        prep = match_span[0]
        inf_verb = match_span[-1]
        if prep.head == verb or inf_verb.head == verb:
            dobj = None
            if hasattr(inf_verb._, 'srl_arg1'):
                dobj = inf_verb._.srl_arg1
            else:
                for tok in span:
                    if tok.dep_ == 'dobj' and tok.head == inf_verb:
                        dobjList = list(t for t in span if t in tok.subtree)
                        start = None
                        end = None
                        for idx,tok in enumerate(span):
                            if tok == dobjList[0]:
                                start = idx
                            elif tok == dobjList[-1]:
                                end = idx
                        if start != None and end != None:
                            dobj = span[start:end+1]
            if dobj == None:
                continue
            else:
                nounPhrases = getNounPhrasefromSpan(prepObjMatcher, dobj, inf_verb, 'dobj')
            if not nounPhrases:
                continue
            else:                      
                [objList, sub_restrictions, sub_inhers] = nounPhrases
                inhers.extend(sub_inhers)
                restrictions.extend(sub_restrictions)
            for obj in objList:
                infList.append([match_span.text, obj])
    return [infList, restrictions, inhers]
