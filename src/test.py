
import spacy
from text_extractor import TextExtractor
# import textacy
from spacy.matcher import Matcher
from spacy.tokens import Token


nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
filename = "../data/en/PSSuniversal_Inst_Manual_21262-EN-07.pdf"

textExtractor1 = TextExtractor(filename)
text = textExtractor1.getText()

# print(text)
print('___________________________________')

# nlp = spacy.blank('en')
# nlp.add_pipe(PySBDFactory(nlp))
doc = nlp(text)
# for sent in doc.sents:
#     print(sent.text)
    
#     print(list(tok.pos_ for tok in sent))
#     print(list(tok.dep_ for tok in sent))
def print_fun(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    span = doc[start:end] 
    print(span.sent.text) 
    print(span.root.text)
    print(list(tok.pos_ for tok in span.sent))
    print(list(tok.dep_ for tok in span.sent))
    print(span)
    print('____________________')

pattern = [{"LEMMA": "be"}, 
            {"TAG": "VBN"},
            {"POS": "ADP"}]
matcher.add("FacebookIs", print_fun, pattern)  # add pattern

matches = matcher(doc)


class SRLComponent(object):
    '''
    A SpaCy pipeline component for SRL
    '''
    
    name = 'Semantic Role Labeler'

    def __init__(self):
        archive = load_archive(self._get_srl_model())
        self.predictor = SemanticRoleLabelerPredictor.from_archive(archive, "semantic-role-labeling")
        Token.set_extension('srl_arg0')
        Token.set_extension('srl_arg1')
        
    def __call__(self, doc):
        # See https://github.com/allenai/allennlp/blob/master/allennlp/service/predictors/semantic_role_labeler.py#L74
        words = [token.text for token in doc]
        for i, word in enumerate(doc):
            if word.pos_ == "VERB":
                verb = word.text
                verb_labels = [0 for _ in words]
                verb_labels[i] = 1
                instance = self.predictor._dataset_reader.text_to_instance(doc, verb_labels)
                output = self.predictor._model.forward_on_instance(instance, -1)
                tags = output['tags']

                # TODO: Tagging/dependencies can be done more elegant 
                if "B-ARG0" in tags:
                    start = tags.index("B-ARG0")
                    end = max([i for i, x in enumerate(tags) if x == "I-ARG0"] + [start]) + 1
                    word._.set("srl_arg0", doc[start:end])

                if "B-ARG1" in tags:
                    start = tags.index("B-ARG1")
                    end = max([i for i, x in enumerate(tags) if x == "I-ARG1"] + [start]) + 1
                    word._.set("srl_arg1", doc[start:end])
        
        return doc