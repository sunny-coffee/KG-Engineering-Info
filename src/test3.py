
# from allennlp.predictors.predictor import Predictor
# predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz")
# result=predictor.predict(
#   sentence="Did Uriah honestly think he could beat the game in under three hours?"
# )
# print(result)

# import os
# from allennlp.predictors.predictor import Predictor
# model_path = "../model/bert-base-srl-2020.11.19.tar"
# if os.path.exists(model_path):
#     predictor = Predictor.from_path(model_path)
#     result=predictor.predict(
#     sentence="Did Uriah honestly think he could beat the game in under three hours?"
#     )
# print(result)


import spacy
nlp = spacy.load('en_core_web_sm')

doc = nlp('I get the car of Tom.')
for tok in doc:
    print(tok, tok.dep_, tok.pos_, tok.head)

# # load NeuralCoref and add it to the pipe of SpaCy's model
# import neuralcoref
# coref = neuralcoref.NeuralCoref(nlp.vocab)
# nlp.add_pipe(coref, name='neuralcoref')

# # You're done. You can now use NeuralCoref the same way you usually manipulate a SpaCy document and it's annotations.
# doc = nlp(u'My sister has a dog. She loves him.')

# print(doc._.has_coref)
# doc._.coref_clusters