
# from allennlp.predictors.predictor import Predictor
# predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz")
# result=predictor.predict(
#   sentence="Did Uriah honestly think he could beat the game in under three hours?"
# )
# print(result)

import os
from allennlp.predictors.predictor import Predictor
from pandas.io.pickle import to_pickle
import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans
from spacy.tokens import Token

class NounMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "NOUN",
            None,
            [{"POS":"PROPN", "OP": "?"},
            {"POS":"ADJ", "OP": "*"},
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
                retokenizer.merge(span, attrs={"lemma": span.lemma_, "_": {"key":span.root.lemma_}})
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
                retokenizer.merge(span, attrs={"LEMMA": span.lemma_})
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
            print(doc[start+1:end])
            spans.append(doc[start-1:end])
        filtered = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in filtered:   
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
        Token.set_extension('srl_arg2', default = None)
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

                    argm_list = []

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

model_path = "../model/bert-base-srl-2020.11.19.tar"
nlp = spacy.load('en_core_web_sm')
merge_ents = nlp.create_pipe("merge_entities")
nlp.add_pipe(merge_ents)
nlp.add_pipe(NounMerger(nlp)) 
# nlp.add_pipe(PrepMerger(nlp))
nlp.add_pipe(DashMerger(nlp))
# nlp.add_pipe(BetweenMerger(nlp))
# nlp.add_pipe(VerbMerger(nlp))
nlp.add_pipe(SRLComponent(model_path), last=True)



text = '''Analogue inputs and outputs plus the inputs and outputs on the counter modules should always be connected using shielded cables.   The module connects the shield to the functional earth via the C-rail. Suppression should not be used to protect the digital semiconductor outputs. Digital semiconductor outputs on the PSSuniversal do not need suppression. 
With FS outputs on the PSSuniversal, suppressions can lead to errors on the on/off tests and test pulses. However, inductive loads that are not switched by the PSSuniversal should be wired with suppression elements for EMC reasons. Care must be taken to avoid interference when installing the unit within an enclosure or wall-mounting.   Earth bars, earth conductors and the housing should be attached to metal parts in order to divert any coupled interference on to large metal areas. For wall-mounting we recommend. that the overall potential surfaces are made of steel.  For varnished or anodised metal parts you should use special contact plates or remove the protective coating. an earth bar for the cable shields can also be 
used as the ground conductor bar.   If an earth bar for the cable shields is to be used as the earth conductor, comply with the latest regulations for earthing an earth bar for the cable shields. '''




doc = nlp(text)
for tok in doc:
    print(tok, tok.lemma_, tok._.key, tok.dep_, tok.pos_)

# print(('and' in [tok.text for tok in doc]) or ('or' in [tok.text for tok in doc]))  

# model_path = "../model/bert-base-srl-2020.11.19.tar"
# if os.path.exists(model_path):
#     predictor = Predictor.from_path(model_path)
#     for sent in doc.sents:

#         result=predictor.predict(sent.text)
#         print(result)


# import spacy
# nlp = spacy.load('en_core_web_sm')

# doc = nlp('I get the car of Tom.')
# for tok in doc:
#     print(tok, tok.dep_, tok.pos_, tok.head)

# # load NeuralCoref and add it to the pipe of SpaCy's model
# import neuralcoref
# coref = neuralcoref.NeuralCoref(nlp.vocab)
# nlp.add_pipe(coref, name='neuralcoref')

# # You're done. You can now use NeuralCoref the same way you usually manipulate a SpaCy document and it's annotations.
# doc = nlp(u'My sister has a dog. She loves him.')

# print(doc._.has_coref)
# doc._.coref_clusters