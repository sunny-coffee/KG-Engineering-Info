# import spacy
# from spacy.util import filter_spans
# from spacy.tokens import Token
# from spacy.matcher import Matcher
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
import neuralcoref
nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

doc = nlp('My sister has a dog. She loves him')

for sent in doc.sents:
    print(sent._.is_coref)
    print(sent._.coref_cluster)

print(doc._.has_coref)
print(doc._.coref_resolved)