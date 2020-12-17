import spacy
from spacy.matcher import Matcher
from spacy.matcher import Matcher
from text_extractor import TextExtractor
from merge_classes import NounMerger, VerbMerger, SRLComponent, PrepMerger


model_path = "../model/bert-base-srl-2020.11.19.tar"
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe(PrepMerger(nlp))
nlp.add_pipe(NounMerger(nlp), last=True)
nlp.add_pipe(VerbMerger(nlp), last=True)
nlp.add_pipe(SRLComponent(model_path), last=True)

# text = 'The connection on the module bus can be disconnected in order to form supply groups. On digital failsafe modules, the periphery supply is used to provide test pulses. Failsafe input/output modules will not start until the periphery supply is connected correctly. On analogue input/output modules, the periphery supply is galvanically isolated from the inputs/outputs.'
text = 'All the base modules and compact modules to the right of the relevant base module must have been moved to the right or have been removed from the rail. All the base modules and compact modules to the right of the relevant base module must have been moved to the right or have been removed from the rail.'
# filename = "../data/en/PSSuniversal_Inst_Manual_21262-EN-07.pdf"

# textExtractor1 = TextExtractor(filename)
# text = textExtractor1.getText()
doc = nlp(text)
# for tok in doc:
#     print(tok, tok._.srl_arg0, tok._.srl_arg1)
# for tok in doc:
#     print(tok, tok.dep_, tok.pos_, tok.head)

## passive
matcher = Matcher(nlp.vocab)

def on_match(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    
    # print(span)
    span = doc[start:end]
    verb = span[-1]
    print(verb)
    print(verb._.srl_arg0)
    print(verb._.srl_arg1)
    print(verb._.srl_arg2)
    print(verb._.srl_argm)
    # print(verb._.srl_arg1.root) 
    # print(getSubjfromSpan(arg1))
    # if verb._.srl_arg2 != None:
    #     print(getPobjfromSpan(verb._.srl_arg2, verb))
    print('________')

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

def getPobjfromSpan(span,verb):
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

pattern1 = [{"LEMMA": "be"}, 
            {"TAG": "VBN"},]
matcher.add("passive", on_match, pattern1)  # add pattern

matcher(doc)


# load NeuralCoref and add it to the pipe of SpaCy's model
# import neuralcoref
# coref = neuralcoref.NeuralCoref(nlp.vocab)
# nlp.add_pipe(coref, name='neuralcoref')

# # You're done. You can now use NeuralCoref the same way you usually manipulate a SpaCy document and it's annotations.
# doc = nlp(u'My sister has a dog. She loves him.')

# print(doc._.coref_clusters[1].mentions[-1]._.coref_cluster.main)
# print(doc._.coref_clusters)