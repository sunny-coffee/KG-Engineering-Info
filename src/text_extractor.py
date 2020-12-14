# import PyPDF2 
# import textract
# import os
from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter,PDFTextExtractionNotAllowed
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams,LTTextLineHorizontal,LTFigure,LTRect,LTLine,LTCurve,LTPage,LTTextLine,LTTextBoxVertical,LTText,LTChar
import re
import spacy
import neuralcoref

nlp1 = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp1)
nlp2 = spacy.load('en_core_web_sm')

class TextExtractor:

    __filename: str

    def __init__(self, filename):
        self.__filename = filename

    def getText(self):
        pd_file = open(self.__filename, "rb")
        parser = PDFParser(pd_file)

        document = PDFDocument()
        parser.set_document(document)
        document.set_parser(parser)

        src = PDFResourceManager()
        device = PDFPageAggregator(src,laparams=LAParams())
        inter = PDFPageInterpreter(src,device)
        pages = document.get_pages()
        text =""
        for page in pages:
            #print(page.contents)
            inter.process_page(page)
            layout = device.get_result()
            for x in layout:                      
                if isinstance(x, LTTextBoxHorizontal):
                    
                    str1 = re.sub(r"\n|\r",' ' , str(x.get_text()))
                    str2 = re.sub(r"-\n|-\r", '',str1)
                    # str2 = re.sub(r"-\n|-\r|The\s|the\s|A\s|a\s|An\s|an\s|All\s|all\s|This\s|That\s|These\s|Those\s|this\s|that\s|these\s|those\s", '',str1)
                    textBox = re.sub(r";|:", '.',str2)
                    if len(textBox)>15 and textBox.endswith('. ') :
                        newText = re.sub(r"}| e.g..*?(,|.) |\(.*?\)|\[.*?\]|– | –|- ","",textBox).replace(' .', '.').replace(' ,', '.').replace('.–', '.')
                        doc1 = nlp1(newText)
                        doc2 = nlp2(doc1._.coref_resolved)
                        for sent in doc2.sents:
                            # print(sent)
                            list_dep = list(tok.dep_ for tok in sent)
                            list_tag = list(tok.tag_ for tok in sent)
                            hasPredicate = ('VB' in list_tag or 'VBD' in list_tag or 'VBP' in list_tag or 'VBZ' in list_tag)
                            hasSubject = ('nsubj' in list_dep or 'nsubjpass' in list_dep)
                            if hasPredicate and hasSubject:
                                text = text + ' ' + sent.text
        return text



    # def getCategory(self):
    #     filename = os.path.basename(self.__filename).split('_')
    #     # print(filename)
    #     category = [filename[0],filename[1]]
    #     # print(category)
    #     return category

    # def getText(self):
    #     pdfFileObj = open(self.__filename,'rb')
 
    #     pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
      
    #     num_pages = pdfReader.numPages
    #     count = 0
    #     text = ""
    
    #     while count < num_pages:
    #         pageObj = pdfReader.getPage(count)
    #         count +=1
    #         text += pageObj.extractText()

    #     if text != "":
    #         text = text
    #     else:
    #         text = textract.process(self.__filename, method='tesseract', language='eng')
        
    #     return text


    # def getText(self):
    #     pdf = PdfFileReader(open(self.__filename, "rb"))
    #     content = ""
    #     for i in range(0, pdf.getNumPages()):
    #         pageObj = pdf.getPage(i)

    #         extractedText = pageObj.extractText()
    #         content += extractedText + "\n"
    #         # return content.encode("ascii", "ignore")
    #     return content

