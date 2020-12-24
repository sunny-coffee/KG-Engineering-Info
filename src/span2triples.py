from spacy.matcher import Matcher

def getSubjfromSpan(prepObjMatcher,span):
        subjList = []
        root_subj = span.root
       
        # subjList.append(span.root.text)
        prepattach = ''
        matches = prepObjMatcher(span)
        for match_id, start, end in matches:
            match_span = span[start:end] 
            if match_span[0].head == root_subj:
                prepattach = prepattach + ' ' + match_span.text
        subjList.append(root_subj.text + prepattach)
        key_subj = root_subj
        if  ('and' in [tok.text for tok in span]) or ('or' in [tok.text for tok in span]):
            for tok in span:
                if tok.head == key_subj and tok.pos_ == "NOUN" and tok.dep_ == "conj":               
                    subjList.append(tok.text + prepattach)
                    key_subj = tok
        return subjList



def getDobjfromSpan(prepObjMatcher,span):
    dobjList = []
    root_obj = span.root
    dobjList.append(root_obj.text)
    for tok in span:
        if tok.head == root_obj and tok.pos_ == "NOUN":
            dobjList.append(tok.text)
    return dobjList

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


def getInffromSpan(infMatcher,span,verb):
    infList = []
    
    matches = infMatcher(span)
    for match_id, start, end in matches:

        match_span = span[start:end] 
        prep = match_span[0]
        if prep.head == verb:
            inf_verb = match_span[-1]
            dobj = inf_verb._.srl_arg1
            infList.append([match_span.text, dobj.text])
    return infList
