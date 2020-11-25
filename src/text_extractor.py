import PyPDF2 
import textract

class TextExtractor:

    __filename: str

    def __init__(self, filename):
        self.__filename = filename

    def getCategory(self):
        pdfFileReader = PyPDF2.PdfFileReader(self.__filename)      
        info = pdfFileReader.getDocumentInfo().title
        category = info.split( )
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
