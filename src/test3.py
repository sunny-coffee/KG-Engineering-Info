import neuralcoref
from allennlp.predictors.predictor import Predictor
predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz")
result=predictor.predict(
  sentence="Did Uriah honestly think he could beat the game in under three hours?"
)
print(result)