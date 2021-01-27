import spacy
from spacy.matcher import Matcher
from spacy.matcher import Matcher
from text_extractor import TextExtractor
from merge_classes import NounMerger, VerbMerger, SRLComponent, PrepMerger
import pandas as pd

model_path = "../model/bert-base-srl-2020.11.19.tar"
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe(PrepMerger(nlp))
nlp.add_pipe(NounMerger(nlp), last=True)
nlp.add_pipe(VerbMerger(nlp), last=True)
nlp.add_pipe(SRLComponent(model_path), last=True)

# text = 'The connection on the module bus can be disconnected in order to form supply groups. On digital failsafe modules, the periphery supply is used to provide test pulses. Failsafe input/output modules will not start until the periphery supply is connected correctly. On analogue input/output modules, the periphery supply is galvanically isolated from the inputs/outputs.'
text = 'All the base modules and compact modules to the right of the relevant base module must have been moved to the right or have been removed from the rail. '
# filename = "../data/en/PSSuniversal_Inst_Manual_21262-EN-07.pdf"
print(text)
# textExtractor1 = TextExtractor(filename)
# text = textExtractor1.getText()
doc = nlp(text)

def getSubjfromSpan(span):
    subjList = []
    root_subj = span.root
    subjList.append(root_subj)
    for tok in span:
        if tok.head == root_subj and tok.pos_ == "NOUN":
            
            subjList.append(tok.text)
    return subjList

def getDobjfromSpan(span):
    dobjList = []
    root_obj = span.root
    dobjList.append(root_obj.text)
    for tok in span:
        if tok.head == root_obj and tok.pos_ == "NOUN":
            dobjList.append(tok.text)
    return dobjList

def getPobjfromSpan(span,verb):
    print(span)
    pobjList = []
    matcher = Matcher(nlp.vocab)
    pattern = [{"POS": "ADP", "DEP": "prep"},
                {"POS": "DET", "OP":"*"},
                {"POS": "NOUN"}]
    matcher.add("POBJ", None, pattern)  # add pattern
    matches = matcher(span)
    for match_id, start, end in matches:
        lit_span = span[start:end]
        # print(span) 
        prep = lit_span[0]
        pobj = lit_span[-1]
        # print(prep.head)
        if prep.head == verb:
            pobjList.append([prep.text, pobj.text])
            # print('!!!!!!!!!!!!')
    return pobjList

matcher = Matcher(nlp.vocab)
pattern1 = [{"LEMMA": "be"}, 
            {"TAG": "VBN"},]
matcher.add("passive", None, pattern1)  # add pattern

matches = matcher(doc)

relations = []
for match_id, start, end in matches:
    
    span = doc[start:end]
    verb = span[-1]

    subjList = getSubjfromSpan(verb._.srl_arg1)
    # print(subjList)
    if len(subjList):
        pass
    else:
        continue
    
    if verb._.srl_arg2 != None:
        pobjList = getPobjfromSpan(verb._.srl_arg2, verb)
        # print(pobjList)
    if len(pobjList):
        for subj in subjList:
            for pobj in pobjList:
                relations.append({"subject":subj ,"relation": 'be ' + verb.text + ' ' + pobj[0], "object": pobj[1]})
    # print(relations)
df = pd.DataFrame(relations)
print(df)