# encoding:utf-8
from PyPDF2 import PdfFileReader, PdfFileWriter

readFile = '151160_Rückschlagventil_GRLA.pdf'
# 获取 PdfFileReader 对象
pdfFileReader = PdfFileReader(readFile)  # 或者这个方式：pdfFileReader = PdfFileReader(open(readFile, 'rb'))
# 获取 PDF 文件的文档信息
documentInfo = pdfFileReader.getDocumentInfo().title
print(documentInfo)
a=documentInfo.split( )
print(a[1])