from spacy.matcher import Matcher

def getNounPhrasefromSpan(prepObjMatcher,span,verb,type):
    # nounPhrasejList = []
    root_noun = span.root
    nounList = []
    prepObjList = []
    nounPrepNounList = []      
    if root_noun.head == verb and type in root_noun.dep_ and root_noun.pos_ == 'NOUN':
        matches = prepObjMatcher(span)

        # conjList = list(tok.head  for tok in span if tok.lemma_ == 'and' or tok.lemma_ == 'or')

        # exsitConj = len(conjList)
        seq = ''
        for match_id, start, end in matches:
            match_span = span[start:end] 
            match_prep = match_span[0]
            # match_pobj = match_span[-1]
            if match_prep.head == root_noun:
                prepObjList.append([match_span[0].lemma_, match_span[-1].lemma_])
                seq = seq + ' ' + match_span.lemma_
                # child_List = match_pobj.children
                # if "and" in list(tok.text for tok in child_List):
                #     for tok in child_List:
                #         if tok.pos_ == "NOUN" and tok.dep_ == "conj":
                #             prepObjList.append([match_span[0].lemma_, tok.lemma_])
                #             seq = seq + ' ' + match_span.lemma_

        nounPrepNounList.append((root_noun.lemma_  + seq).strip())
        nounList.append(root_noun.lemma_)
        key_noun = root_noun

        if  ('and' in [tok.text for tok in span]) or ('or' in [tok.text for tok in span]):
            for tok in span:
                if tok.head == key_noun and tok.pos_ == "NOUN" and tok.dep_ == "conj":               
                    nounList.append(tok.lemma_)
                    nounPrepNounList.append((tok.lemma_ + seq).strip())
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
     
                    prepObjList.append([match_span[0].lemma_, match_span[-1].lemma_])
                    seq = seq + ' ' + match_span.lemma_
            nounPrepNoun = (prepObj.lemma_  + seq).strip()
            pobjList.append([prep.lemma_, nounPrepNoun])
            # print(prepObjList)
            if len(prepObjList):
                triples.append({"subject":nounPrepNoun ,"relation": 'is_a', "object": prepObj.lemma_})
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
                infList.append([match_span.lemma_, obj])
    return [infList, triples]
