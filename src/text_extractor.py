from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import re
import spacy
import neuralcoref


"""
The method to recognize texts from PDF is coded in this file. 
"""

nlp1 = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp1)
nlp2 = spacy.load('en_core_web_sm')

class TextExtractor:

    __filename: str

    def __init__(self, filename):
        self.__filename = filename

    def getText(self):
        text =""
        for page in extract_pages(self.__filename):
            for x in page:                      
                if isinstance(x, LTTextContainer):           
                    str1 = re.sub(r"\n|\r",' ' , str(x.get_text()))
                    str2 = re.sub(r"-\n|-\r", '',str1)
                    textBox = re.sub(r";|:", '.',str2)
                    if len(textBox)>15 and textBox.endswith('. ') :
                        newText = re.sub(r"}| e.g..*?(,|.) |\(.*?\)|\[.*?\]|– | –|- ","",textBox).replace(' .', '.').replace(' ,', '.').replace('.–', '.')
                        doc1 = nlp1(newText)
                        doc2 = nlp2(doc1._.coref_resolved)
                        for sent in doc2.sents:
                            list_dep = list(tok.dep_ for tok in sent)
                            list_tag = list(tok.tag_ for tok in sent)
                            hasPredicate = ('VB' in list_tag or 'VBD' in list_tag or 'VBP' in list_tag or 'VBZ' in list_tag, 'VBG' in list_tag, 'VBN' in list_tag)
                            hasSubject = ('nsubj' in list_dep or 'nsubjpass' in list_dep)
                            if hasPredicate and hasSubject:
                                text = text + ' ' + sent.text
        return text
