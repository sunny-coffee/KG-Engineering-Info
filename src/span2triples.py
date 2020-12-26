from spacy.matcher import Matcher

def getNounPhrasefromSpan(prepObjMatcher,span,verb,type):
    # nounPhrasejList = []
    root_noun = span.root
    nounList = []
    prepObjList = []
    nounPrepNounList = []      
    if root_noun.head == verb and type in root_noun.dep_:
        matches = prepObjMatcher(span)
        seq = ''
        for match_id, start, end in matches:
            match_span = span[start:end] 
            if match_span[0].head == root_noun:
                prepObjList.append([match_span[0].text, match_span[-1].text])
                seq = seq + ' ' + match_span.text
        nounPrepNounList.append((root_noun.text  + seq).strip())
        nounList.append(root_noun.text)
        key_noun = root_noun
        if  ('and' in [tok.text for tok in span]) or ('or' in [tok.text for tok in span]):
            for tok in span:
                if tok.head == key_noun and tok.pos_ == "NOUN" and tok.dep_ == "conj":               
                    nounList.append(tok.text)
                    nounPrepNounList.append((tok.text + seq).strip())
                    key_noun = tok
    if not len(nounList):            
        return False
    triples = []
    if len(prepObjList):
        for i, npn in enumerate(nounPrepNounList):
            triples.append({"subject":npn ,"relation": 'is_a', "object": nounList[i]})
            for pobj in prepObjList:
                triples.append({"subject":npn ,"relation": pobj[0], "object": pobj[1]})
    
    return [nounPrepNounList, triples]


def getPobjfromSpan(prepObjMatcher,span,verb):
    pobjList = []
    triples = []
    matches1 = prepObjMatcher(span)
    for match_id, start, end in matches1:
        match_span1 = span[start:end] 
        prep = match_span1[0]
        prepObj = match_span1[-1]
        if prep.head == verb:
            # print('2222')
            prepObjList = []
            matches2 = prepObjMatcher(span)
            seq = ''
            for match_id, start, end in matches2:
                match_span = span[start:end] 
                if match_span[0].head == prepObj:
     
                    prepObjList.append([match_span[0].text, match_span[-1].text])
                    seq = seq + ' ' + match_span.text
            nounPrepNoun = (prepObj.text  + seq).strip()
            pobjList.append([prep.text, nounPrepNoun])
            print(prepObjList)
            if len(prepObjList):
                triples.append({"subject":nounPrepNoun ,"relation": 'is_a', "object": prepObj})
                for pobj in prepObjList:
                    triples.append({"subject":nounPrepNoun ,"relation": pobj[0], "object": pobj[1]})
    return [pobjList, triples]


def getInffromSpan(infMatcher,prepObjMatcher,span,verb):
    infList = []
    triples = []
    matches = infMatcher(span)
    for match_id, start, end in matches:

        match_span = span[start:end] 
        prep = match_span[0]
        if prep.head == verb:
            inf_verb = match_span[-1]
            dobj = inf_verb._.srl_arg1
            if dobj == None:
                continue
            else:
                nounPhrases = getNounPhrasefromSpan(prepObjMatcher, dobj, inf_verb, 'dobj')
            if not nounPhrases:
                continue
            else:                      
                [objList, sub_triples] = nounPhrases
                triples.extend(sub_triples)
            for obj in objList:
                infList.append([match_span.text, obj])
    return [infList, triples]
