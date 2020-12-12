# import PyPDF2 
# import textract
# import os
from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter,PDFTextExtractionNotAllowed
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams,LTTextLineHorizontal,LTFigure,LTRect,LTLine,LTCurve,LTPage,LTTextLine,LTTextBoxVertical,LTText,LTChar
import re
import spacy

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
                    textBox = str(x.get_text()).replace('\n', '').replace('\r', '').replace('-\n', '').replace('-\r', '').replace(';', '.').replace(':', '.')
                    
                    if len(textBox)>15 and textBox.endswith('.') :
                        newText = re.sub(r"}| e.g..*?(,|.) |\(.*?\)|\[.*?\]|– || –","",textBox).replace(' .', '.').replace(' ,', '.').replace('.–', '.')
                        text = text + newText
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

