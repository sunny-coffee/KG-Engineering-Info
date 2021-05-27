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
                retokenizer.merge(span, attrs={"LEMMA": span.lemma_})
        return doc   


class NounMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "NOUN",
            None,
            [{"POS":"PROPN", "OP": "?"},
            {"DEP":"amod", "OP": "*"},
            {"DEP":"nummod", "OP": "*"}, 
            {"POS": "NOUN", "OP": "+"}]
        )
        Token.set_extension('key', default = None)

    def __call__(self, doc):
        # This method is invoked when the component is called on a Doc
        matches = self.matcher(doc)
        spans = []  # Collect the matched spans here
        
        for match_id, start, end in matches:
            spans.append(doc[start:end])
        filtered = filter_spans(spans)
        with doc.retokenize() as retokenizer:
            for span in filtered:  
                # print(span)
                if len(span) >=2:
                    span_lemma = span[0:-1].text + ' ' + span[-1].lemma_
                else:
                    span_lemma = span.lemma_
                retokenizer.merge(span, attrs={"lemma": span_lemma, "_": {"key":span.root.lemma_}})
        return doc

class BetweenMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "BETWEEN",
            None,
            [{"LEMMA":"between"},
            {"POS": "DET", "OP":"*"},
            {"POS": "NOUN"},
            {"LEMMA":"and"},
            {"POS": "DET", "OP":"*"},
            {"POS": "NOUN"}]
        )

    def __call__(self, doc):
        # This method is invoked when the component is called on a Doc
        matches = self.matcher(doc)
        spans = []  # Collect the matched spans here
        
        for match_id, start, end in matches:
            spans.append(doc[start+1:end])
        filtered = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in filtered:   
                retokenizer.merge(span, attrs={"LEMMA": span.lemma_})
        return doc

class DashMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "DASH",
            None,
            [{"LEMMA":"-"}]
        )
        self.matcher.add(
            "SLASH",
            None,
            [{"LEMMA":"/"}]
        )

    def __call__(self, doc):
        # This method is invoked when the component is called on a Doc
        matches = self.matcher(doc)
        spans = []  # Collect the matched spans here
        
        for match_id, start, end in matches:
            if not doc[start].whitespace_ and not doc[start-1].whitespace_:
                spans.append(doc[start-1:end+1])
        filtered = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in filtered:
                retokenizer.merge(span, attrs={"LEMMA": span[0].lemma_ + span[1].lemma_ + span[2].lemma_})
        return doc



class VerbMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "Verb",
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
                retokenizer.merge(span, attrs={"LEMMA": span.lemma_})
        return doc

class VerbPhraseMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "VerbPhrase",
            None,
            [{"TEXT":"be", "OP": "?"},
            {"POS":"VERB"}, 
            {"TAG":"RB" , "OP": "*"},
            {"LEMMA": "to", "POS": "PART", "OP": "?"}]
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
                if len(span) > 1:
                    retokenizer.merge(span, attrs={"LEMMA": span[0].lemma_ + ' ' + span[1:end].text})
                else:
                    retokenizer.merge(span, attrs={"LEMMA": span.lemma_})
        return doc

class LongestVerbMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "LongestVerb",
            None,
            [{"POS":"VERB", "OP": "+"}]
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
                if len(span) > 1:
                    retokenizer.merge(span, attrs={"LEMMA": span[0].lemma_ + ' ' + span[1:end].text})
                else:
                    retokenizer.merge(span, attrs={"LEMMA": span.lemma_})
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
        # Token.set_extension('srl_arg2', default = None)
        Token.set_extension('srl_argm', default = [])

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
                        if "I-ARG0" in tags:
                            end = max([i for i, x in enumerate(tags) if x == "I-ARG0"] + [start]) + 1
                        else:
                            end = start + 1
                        word._.set("srl_arg0", sent[start:end])

                    if "B-ARG1" in tags:
                        start = tags.index("B-ARG1")
                        if "I-ARG1" in tags:
                            end = max([i for i, x in enumerate(tags) if x == "I-ARG1"] + [start]) + 1
                        else:
                            end = start + 1
                        word._.set("srl_arg1", sent[start:end])
                    
                    # if "B-ARG2" in tags:
                    #     start = tags.index("B-ARG2")
                    #     if "I-ARG2" in tags:
                    #         end = max([i for i, x in enumerate(tags) if x == "I-ARG2"] + [start]) + 1
                    #     else:
                    #         end = start + 1
                    #     word._.set("srl_arg2", sent[start:end])

                    argm_list = []

                    if "B-ARG2" in tags:
                        start = tags.index("B-ARG2")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARG2"] + [start]) + 1
                        argm_list.append(sent[start:end])

                    if "B-ARG3" in tags:
                        start = tags.index("B-ARG3")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARG3"] + [start]) + 1
                        argm_list.append(sent[start:end])
                    
                    if "B-ARG4" in tags:
                        start = tags.index("B-ARG4")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARG4"] + [start]) + 1
                        argm_list.append(sent[start:end])

                    if "B-ARGM-MNR" in tags:
                        start = tags.index("B-ARGM-MNR")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARGM-MNR"] + [start]) + 1
                        argm_list.append(sent[start:end])
                    
                    if "B-ARGM-LOC" in tags:
                        start = tags.index("B-ARGM-LOC")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARGM-LOC"] + [start]) + 1
                        argm_list.append(sent[start:end])

                    if "B-ARGM-TMP" in tags:
                        start = tags.index("B-ARGM-TMP")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARGM-TMP"] + [start]) + 1
                        argm_list.append(sent[start:end])

                    if "B-ARGM-PRP" in tags:
                        start = tags.index("B-ARGM-PRP")
                        end = max([i for i, x in enumerate(tags) if x == "I-ARGM-PRP"] + [start]) + 1
                        argm_list.append(sent[start:end])

                    word._.set("srl_argm", argm_list)
                    

        return doc
