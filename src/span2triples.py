from spacy.matcher import Matcher

def getSubjfromSpan(prepObjMatcher,span,verb):
    subjPobjList = []
    root_subj = span.root      
    if root_subj.head == verb:
        subjList = []
        pobjList = []
        matches = prepObjMatcher(span)
        for match_id, start, end in matches:
            match_span = span[start:end] 
            if match_span[0].head == root_subj:
                pobjList.append(match_span.text)
        subjList.append(root_subj.text)
        key_subj = root_subj
        if  ('and' in [tok.text for tok in span]) or ('or' in [tok.text for tok in span]):
            for tok in span:
                if tok.head == key_subj and tok.pos_ == "NOUN" and tok.dep_ == "conj":               
                    subjList.append(tok.text)
                    key_subj = tok
        for subj in subjList:
            subjPobj = subj
            for pobj in pobjList:
                subjPobj = subjPobj + ' ' + pobj
            subjPobjList.append(subjPobj.strip())
    return subjPobjList



def getDobjfromSpan(prepObjMatcher,span,verb):
    objList = []
    root_subj = span.root      
    if root_subj.head == verb:
        prepattach = ''
        matches = prepObjMatcher(span)
        for match_id, start, end in matches:
            match_span = span[start:end] 
            if match_span[0].head == root_subj:
                prepattach = prepattach + ' ' + match_span.text
        objList.append(root_subj.text + prepattach)
        key_obj = root_subj
        if  ('and' in [tok.text for tok in span]) or ('or' in [tok.text for tok in span]):
            for tok in span:
                if tok.head == key_obj and tok.pos_ == "NOUN" and tok.dep_ == "conj":               
                    objList.append(tok.text + prepattach)
                    key_obj = tok
    return objList

def getPobjfromSpan(prepObjMatcher,span,verb):
    pobjList = []
    
    matches = prepObjMatcher(span)
    for match_id, start, end in matches:
        # print('11111')
        match_span = span[start:end] 
        prep = match_span[0]
        pobj = match_span[-1]
        if prep.head == verb:
            # print('2222')
            pobjList.append([prep.text, pobj.text])
    return pobjList


def getInffromSpan(infMatcher,prepObjMatcher,span,verb):
    infList = []
    
    matches = infMatcher(span)
    for match_id, start, end in matches:

        match_span = span[start:end] 
        prep = match_span[0]
        if prep.head == verb:
            inf_verb = match_span[-1]
            dobj = inf_verb._.srl_arg1
            objList = getDobjfromSpan(prepObjMatcher,dobj,inf_verb)
            for obj in objList:
                infList.append([match_span.text, obj])
    return infList
