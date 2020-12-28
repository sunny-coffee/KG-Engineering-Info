
# from allennlp.predictors.predictor import Predictor
# predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz")
# result=predictor.predict(
#   sentence="Did Uriah honestly think he could beat the game in under three hours?"
# )
# print(result)

import os
from allennlp.predictors.predictor import Predictor
import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans

class NounMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "NOUN",
            None,
            [{"POS":"ADJ", "OP": "*"},
            {"DEP":"nummod", "OP": "*"}, 
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

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe(NounMerger(nlp))
nlp.add_pipe(DashMerger(nlp))
nlp.add_pipe(BetweenMerger(nlp))



text = 'A different potential between the source and interference sink creates an electrical field.'





doc = nlp(text)
for tok in doc:
    print(tok.lemma_, tok.dep_,tok.pos_,tok.tag_,tok.head)

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