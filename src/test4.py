import spacy

nlp = spacy.load('en_core_web_sm')

# txt = 'Using the screwdriver, press the actuator button down as far as it will go.'

# doc = nlp(txt)
# for sent in doc.sents:
#     print(sent.root.pos_ == 'VERB')
# # statements = textacy.extract.semistructured_statements(doc, "this")
# # for statement in statements:
# #     subject, verb, fact = statement
# #     print(f" - {fact}",f" - {verb}")
# list_dep = list(tok.dep_ for tok in doc)
# print('nsubj' in list_dep or 'nsubjpass' in list_dep)

# print(list(tok.dep_ for tok in doc))

text = 'I am going to go to his park.'
doc = nlp(text)
print(doc[2:10].start_char)


# load NeuralCoref and add it to the pipe of SpaCy's model
# import neuralcoref
# coref = neuralcoref.NeuralCoref(nlp.vocab)
# nlp.add_pipe(coref, name='neuralcoref')

# # You're done. You can now use NeuralCoref the same way you usually manipulate a SpaCy document and it's annotations.
# doc = nlp(u'My sister has a dog. She loves him.')

# print(doc._.coref_clusters[1].mentions[-1]._.coref_cluster.main)
# print(doc._.coref_clusters)