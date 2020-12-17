from spacy.util import filter_spans
from spacy.tokens import Token
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
import os
from allennlp.predictors.predictor import Predictor
import json

class PrepMerger(object):
    def __init__(self, nlp):
        self.matcher = PhraseMatcher(nlp.vocab)
        with open("phrasal_preposition.json") as f:
            PREPS = json.loads(f.read())
        self.matcher.add("PREPOSITION", None, *list(nlp.pipe(PREPS)))
    def __call__(self, doc):
        matches = self.matcher(doc)
        spans = []        
        for match_id, start, end in matches:
            spans.append(doc[start:end])
        filtered = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in filtered:
                retokenizer.merge(span)
        return doc   


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
        for sent in doc.sents:
            
            words = [token.text for token in sent]
            for i, word in enumerate(sent):
                if word.pos_ == "VERB":
                    verb_labels = [0 for _ in words]
                    verb_labels[i] = 1
                    instance = self.predictor._dataset_reader.text_to_instance(sent, verb_labels)
                    
                    output = self.predictor._model.forward_on_instance(instance)
                    tags = output['tags']
                    # print(tags)

                    # TODO: Tagging/dependencies can be done more elegant 
                    if "B-ARG0" in tags:
                        start = tags.index("B-ARG0")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARG0"] + [start]) + 1
                        word._.set("srl_arg0", sent[start:end])

                    if "B-ARG1" in tags:
                        start = tags.index("B-ARG1")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARG1"] + [start]) + 1
                        word._.set("srl_arg1", sent[start:end])
                    
                    if "B-ARG2" in tags:
                        start = tags.index("B-ARG2")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARG2"] + [start]) + 1
                        word._.set("srl_arg2", sent[start:end])

                    if "B-ARGM-TMP" in tags:
                        start = tags.index("B-ARGM-TMP")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARGM-TMP"] + [start]) + 1
                        word._.set("srl_argm", sent[start:end])
                    

        return doc
