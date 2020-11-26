import PyPDF2 
import textract
import os

class TextExtractor:

    __filename: str

    def __init__(self, filename):
        self.__filename = filename

    def getCategory(self):
        filename = os.path.basename(self.__filename).split('_')
        # print(filename)
        category = [filename[0],filename[1]]
        # print(category)
        return category

    def getText(self):
        pdfFileObj = open(self.__filename,'rb')
 
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
      
        num_pages = pdfReader.numPages
        count = 0
        text = ""
    
        while count < num_pages:
            pageObj = pdfReader.getPage(count)
            count +=1
            text += pageObj.extractText()

        if text != "":
            text = text
        else:
            text = textract.process(self.__filename, method='tesseract', language='eng')
        
        return text
