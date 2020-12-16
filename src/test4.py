import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans
from spacy.tokens import Token
from spacy.matcher import Matcher
import os
from allennlp.predictors.predictor import Predictor


class NounMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "NOUN",
            None,
            [{"DEP":"amod", "OP": "*"}, 
            {"POS": "NOUN", "OP": "+"}]
        )

    def __call__(self, doc):
        # This method is invoked when the component is called on a Doc
        matches = self.matcher(doc)
        spans = []  # Collect the matched spans here
        
        for match_id, start, end in matches:
            spans.append(doc[start:end])
        filtered = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in filtered:
                retokenizer.merge(span)
        return doc

class VerbMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "NOUN",
            None,
            [{"POS":"VERB"}, 
            {"POS": "ADP", "DEP": "prt"}]
        )

    def __call__(self, doc):
        # This method is invoked when the component is called on a Doc
        matches = self.matcher(doc)
        spans = []  # Collect the matched spans here
        
        for match_id, start, end in matches:
            spans.append(doc[start:end])
        filtered = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in filtered:
                retokenizer.merge(span)
        return doc

class SRLComponent(object):

    def __init__(self, model_path):
        self.model_path = model_path
        if os.path.exists(self.model_path):
            self.predictor = Predictor.from_path(model_path)
        else:
            self.predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz")
        Token.set_extension('srl_arg0', default = None)
        Token.set_extension('srl_arg1', default = None)
        Token.set_extension('srl_arg2', default = None)
        Token.set_extension('srl_argm', default = None)

    def __call__(self, doc):
        words = [token.text for token in doc]
        for i, word in enumerate(doc):
            if word.pos_ == "VERB":
                verb_labels = [0 for _ in words]
                verb_labels[i] = 1
                instance = self.predictor._dataset_reader.text_to_instance(doc, verb_labels)
                
                output = self.predictor._model.forward_on_instance(instance)
                tags = output['tags']
                # print(tags)

                # TODO: Tagging/dependencies can be done more elegant 
                if "B-ARG0" in tags:
                    start = tags.index("B-ARG0")
                    end = max([i for i, x in enumerate(tags) if x == "I-ARG0"] + [start]) + 1
                    word._.set("srl_arg0", doc[start:end])

                if "B-ARG1" in tags:
                    start = tags.index("B-ARG1")
                    end = max([i for i, x in enumerate(tags) if x == "I-ARG1"] + [start]) + 1
                    word._.set("srl_arg1", doc[start:end])
                
                if "B-ARG2" in tags:
                    start = tags.index("B-ARG2")
                    end = max([i for i, x in enumerate(tags) if x == "I-ARG2"] + [start]) + 1
                    word._.set("srl_arg2", doc[start:end])

                if "B-ARGM-TMP" in tags:
                    start = tags.index("B-ARGM-TMP")
                    end = max([i for i, x in enumerate(tags) if x == "I-ARGM-TMP"] + [start]) + 1
                    word._.set("srl_argm", doc[start:end])

        return doc


model_path = "../model/bert-base-srl-2020.11.19.tar"
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe(NounMerger(nlp), last=True)
nlp.add_pipe(VerbMerger(nlp), last=True)
nlp.add_pipe(SRLComponent(model_path), last=True)

# text = 'All the base modules and compact modules to the right of the relevant base module must have been moved to the right or have been removed from the rail.'
text = 'All the base modules and compact modules to the right of the relevant base module must have been moved to the right or have been removed from the rail.'
doc = nlp(text)
# for tok in doc:
#     print(tok, tok._.srl_arg0, tok._.srl_arg1)
for tok in doc:
    print(tok, tok.dep_, tok.pos_, tok.head)

## passive
matcher = Matcher(nlp.vocab)

def print_fun(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    
    # print(span)
    verb = doc[end-1]
    arg1 = verb._.srl_arg1

    print('________')
    print(verb._.srl_arg1.root) 
    print(getSubjfromSpan(arg1))
    print(verb)
    if verb._.srl_arg2 != None:
        print(getPobjfromSpan(verb._.srl_arg2, verb))
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
matcher.add("passive", print_fun, pattern1)  # add pattern

matcher(doc)


# load NeuralCoref and add it to the pipe of SpaCy's model
# import neuralcoref
# coref = neuralcoref.NeuralCoref(nlp.vocab)
# nlp.add_pipe(coref, name='neuralcoref')

# # You're done. You can now use NeuralCoref the same way you usually manipulate a SpaCy document and it's annotations.
# doc = nlp(u'My sister has a dog. She loves him.')

# print(doc._.coref_clusters[1].mentions[-1]._.coref_cluster.main)
# print(doc._.coref_clusters)