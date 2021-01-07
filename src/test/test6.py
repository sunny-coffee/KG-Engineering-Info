from owlready2 import DatatypeProperty, FunctionalProperty, get_ontology, Inverse, \
     InverseFunctionalProperty, ObjectProperty, Thing, TransitiveProperty, SymmetricProperty,types
import pandas as pd
# import camelot
import re

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser


filename = "../data/en/data_sheet/Pilz/RevPi_DIO_Data_Sheet_1004859-EN-01.pdf"

pd_file = open(filename, "rb")
parser = PDFParser(pd_file)

document = PDFDocument(parser)
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
            str1 = x.get_text()
            
            print(re.findall(r"a(.+?)b", str))
            # Article\sNo.::\s(\d{6})


IRI = "http://example.org/engineering-info.owl"
FILE = "test6.owl"

# tables = camelot.read_pdf(filename, pages="1-end", flavor='lattice')
# for table in tables:
#     pd.set_option('display.max_rows', None)
#     tdf = table.df
#     # pd.set_option('display.max_columns', None)
#     if tdf.iloc[0,0] == 'Product type' and tdf.iloc[0,-1] == 'Order no.':
#         print(tdf)
#         attrList = list(tdf.iloc[0,i] for i in range(tdf.shape[1]))
#         for attr in attrList:

#         for index, row in tdf.iterrows():
#             print(row[0].replace('\n', ' '))
        # tdf.columns = tdf.iloc[0].tolist
        # print(tdf)



# onto = get_ontology(IRI)
# with onto:
#     # classes
#     class product_Pilz(Thing):
#         comment = ["parent class of all Pilz products"]
#     class PSEN_Cable_M8_M8_8p(product_Pilz):
#         pass
#     class hasAttributeOf(ObjectProperty):
#         domain = [PSEN_Cable_M8_M8_8p]
#         range = [str]
#     for table in tables:
#         pd.set_option('display.max_rows', None)
#         tdf = table.df
#         print(tdf)




        # attrList = list(tdf.iloc[0,i].replace("-\n", "").replace("\n", " ").replace("  ", " ").replace(" ", "_") for i in range(tdf.shape[1]))
        # if ('Product_type' in attrList or 'Type' in attrList) and 'Order_no.' in attrList:
        #     tdf.columns = attrList
        #     tdf.drop(index=[0], inplace=True)
        #     print(tdf)
        #     for attr in attrList:
        #         if len(attr):
        #             attrClass = types.new_class(attr,(Thing,))
        #             relation = types.new_class('hasAttributeOf'+attr,(hasAttributeOf,))
        #             relation.domain.append(PSEN_Cable_M8_M8_8p)
        #             relation.range.append(attrClass)
        #     for index, row in tdf.iterrows():
        #         product_instance = PSEN_Cable_M8_M8_8p(row['Order_no.'].replace(' ','_'))
        #         for attr in attrList:
        #             if attr != 'Order_no.' and len(attr):
        #                 if len(row[attr]):
        #                     attr_instance = getattr(onto, attr)(re.sub(r"\s|,|-|/", '_',row[attr].replace('-\n','').replace('\n',' ')))
        #                     getattr(product_instance, 'hasAttributeOf'+attr).append(attr_instance)
# onto.save(file=FILE)