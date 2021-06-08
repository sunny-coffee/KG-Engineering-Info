# import spacy
# from text_extractor import TextExtractor


# class VerbPhraseMerger(object):
#     def __init__(self, nlp):
#         self.matcher = Matcher(nlp.vocab)
#         self.matcher.add(
#             "VerbPhrase",
#             None,
#             [{"LEMMA":"be", "OP": "?"},
#             {"POS":"VERB"}, 
#             {"TAG":"RB" , "OP": "*"},
#             {"LEMMA": "to", "POS": "PART", "OP": "?"}]
#         )

#     def __call__(self, doc):
#         # This method is invoked when the component is called on a Doc
#         matches = self.matcher(doc)
#         spans = []  # Collect the matched spans here
        
#         for match_id, start, end in matches:
#             spans.append(doc[start:end])
#         filtered = filter_spans(spans)

#         with doc.retokenize() as retokenizer:
#             for span in filtered:
#                 if len(span) > 1:
#                     retokenizer.merge(span, attrs={"LEMMA": span[0].lemma_ + ' ' + span[1:end].text})
#                 else:
#                     retokenizer.merge(span, attrs={"LEMMA": span.lemma_})
#         return doc

# class LongestVerbMerger(object):
#     def __init__(self, nlp):
#         self.matcher = Matcher(nlp.vocab)
#         self.matcher.add(
#             "LongestVerb",
#             None,
#             [{"POS":"VERB", "OP": "+"}]
#         )

#     def __call__(self, doc):
#         # This method is invoked when the component is called on a Doc
#         matches = self.matcher(doc)
#         spans = []  # Collect the matched spans here
        
#         for match_id, start, end in matches:
#             spans.append(doc[start:end])
#         filtered = filter_spans(spans)

#         with doc.retokenize() as retokenizer:
#             for span in filtered:
#                 if len(span) > 1:
#                     retokenizer.merge(span, attrs={"LEMMA": span[0].lemma_ + ' ' + span[1:end].text})
#                 else:
#                     retokenizer.merge(span, attrs={"LEMMA": span.lemma_})
#         return doc

# nlp = spacy.load('en_core_web_sm')
# nlp.add_pipe(VerbPhraseMerger(nlp))
# nlp.add_pipe(LongestVerbMerger(nlp))

# text = '''Earth, bars, conductors and the housing should be attached to metal parts in order to divert any coupled interference on to large metal areas.'''

# doc = nlp(text)

# for tok in doc:
#     # print(tok.text, tok.lemma_, tok.dep_, tok.pos_, tok.tag_, list(t.text for t in tok.subtree), tok.head, list(t.text for t in tok.ancestors))
#     print(tok, tok.head)

# # li = []
# # li.append({'a':1, 'b':[1]})
# # print(li[-1]['b'])
# import spacy
# from spacy import displacy
# from spacy.tokens import Token

# Token.set_extension('srl_arg0', default = None)
# nlp = spacy.load("en_core_web_sm")
# # doc = nlp(' This operating manual explains the function and operation, describes the installation and provides guidelines on how to connect the product.')
# doc = nlp('a b')
# # for sent in doc.sents:
# #     for tok in sent:
# #         print(tok)
# #     print(sent)
# # for idx,item in enumerate(doc):
# #     print(item)
# # print(hasattr(span[2],'srl_arg0'))

# # a =[1,2,3]
# # a.remove(1,2)
# # print(a)
# print(doc[0:-1])
# for tok in doc:
#     print(tok, tok.dep_, tok.pos_, tok.head)

import spacy
from spacy.util import filter_spans
from spacy.tokens import Token, Span
from spacy.matcher import Matcher
from span2triples import getNounPhrasefromSpan
# import neuralcoref
nlp = spacy.load('en_core_web_sm')
# neuralcoref.add_to_pipe(nlp)

class CopulaMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "Copula",
            None,
            [{"LEMMA":"be"}, 
            {"POS": "ADJ"}]
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

class NounMerger(object):
    def __init__(self, nlp):
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "NOUN",
            None,
            [{"POS":"PROPN", "OP": "?"},
            {"DEP":"nummod", "OP": "*"},
            {"POS":"ADV", "OP": "*"},
            {"POS":"ADJ", "OP": "*"}, 
            {"POS":"NUM", "OP": "*"},
            {"POS": "NOUN", "OP": "+"},
            {"TAG": "NNP", "OP": "*"}]
        )
        Token.set_extension('key', default = None)

    def __call__(self, doc):
        # This method is invoked when the component is called on a Doc
        matches = self.matcher(doc)
        spans = []  # Collect the matched spans here
        
        for match_id, start, end in matches:
            spans.append(doc[start:end])
        filtered = filter_spans(spans)
        # print(filtered)
        with doc.retokenize() as retokenizer:
            for span in filtered:  
                # print(span)
                if len(span) >=2:
                    span_lemma = span[0:-1].text + ' ' + span[-1].lemma_
                else:
                    span_lemma = span.lemma_
                retokenizer.merge(span, attrs={"lemma": span_lemma, "_": {"key":span.root.lemma_}})
        return doc

nlp.add_pipe(CopulaMerger(nlp))
nlp.add_pipe(NounMerger(nlp))

doc = nlp(' The error code can consist of up to 4 digits')
prepObjMatcher = Matcher(nlp.vocab)
pattern = [{"POS": "ADP"},
            {"POS": "DET", "OP":"*"},
            {"POS": "NOUN"}]
prepObjMatcher.add("pobj", None, pattern)

for tok in doc:
    # for tok in sent:
    print(tok.i, tok.text, tok.lemma_, tok.dep_, tok.pos_, tok.tag_, tok.head)
# print(doc[0])
# print(doc[1])
# print(getNounPhrasefromSpan(prepObjMatcher, doc[0:8],doc[9],'all'))
# print(type(doc[0]) == Token)


