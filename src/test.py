# from pysbd.utils import PySBDFactory
import spacy
from text_extractor import TextExtractor
nlp = spacy.load('en_core_web_sm')

filename = "../data/en/PSSuniversal_Inst_Manual_21262-EN-07.pdf"

textExtractor1 = TextExtractor(filename)
text = textExtractor1.getText()
print(text)
print('___________________________________')

# nlp = spacy.blank('en')
# nlp.add_pipe(PySBDFactory(nlp))

doc = nlp(text)
for sent in doc.sents:
    print(sent)
# # [My name is Jonas E. Smith., Please turn to p. 55.]


                        # text = ""
                        # for y in x:
                        #         if isinstance(y, LTTextLine):
                        #                 # print('y',type(y))
                        #                 # text = text + str(y.get_text()).replace('\n', '').replace('\r', '')
                        #                 for z in y:
                        #                         if isinstance(z,LTChar):
                        #                                 # print('z',type(z))
                        #                                 if max < z.adv:
                        #                                         max = z.adv
                                        
                # if len(text) >= 30:
                #         print(text)
                #         print('---------------------')
# outlines = document.get_outlines()
# for (level,title,dest,a,se) in outlines:
#     print (level, title)

# import spacy
# import neuralcoref

# nlp = spacy.load("en_core_web_sm")
# neuralcoref.add_to_pipe(nlp)
# doc = nlp('My sister has a dog. She loves him.I don\'t like apple. It is too sweet. But My mother likes it. She says that she likes the thing sweet.')
# span = doc[6:7]
# print(span)
# print(span._.coref_cluster)

# print(span._.coref_cluster.main)