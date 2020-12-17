from spacy.matcher import Matcher

def getSubjfromSpan(span):
        subjList = []
        root_subj = span.root
        subjList.append(root_subj)
        for tok in span:
            if tok.head == root_subj and tok.pos_ == "NOUN":
                
                subjList.append(tok)
        return subjList

def getDobjfromSpan(span):
    dobjList = []
    root_obj = span.root
    dobjList.append(root_obj.text)
    for tok in span:
        if tok.head == root_obj and tok.pos_ == "NOUN":
            dobjList.append(tok.text)
    return dobjList

def getPobjfromSpan(nlp,span,verb):
    pobjList = []
    matcher = Matcher(nlp.vocab)
    pattern = [{"POS": "ADP", "DEP": "prep"},
                {"POS": "DET", "OP":"*"},
                {"POS": "NOUN"},]
    matcher.add("pobj", None, pattern)  # add pattern
    matches = matcher(span)
    for match_id, start, end in matches:
        span = span[start:end] 
        prep = span[0]
        pobj = span[-1]
        if prep.head == verb:
            pobjList.append(prep.text + pobj.text)

    return pobjList
