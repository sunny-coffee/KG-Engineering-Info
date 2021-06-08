from os import replace
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextContainer, LTChar, LTTextLine
import camelot
import re
from owlready2 import DatatypeProperty, FunctionalProperty, get_ontology, Inverse, \
     InverseFunctionalProperty, ObjectProperty, Thing, TransitiveProperty, SymmetricProperty,types
import pandas as pd

filename = "../data/en/data_sheet/Pilz/RevPi_Core_3_Data_Sheet_1004848-EN-01.pdf"

def processStr(str):
    str1 = re.sub(r"\s+|,|-|/|\(|\)|:|\|", ' ',str)
    str2 = str1.replace('°C',' degree').replace(' x ','x').replace('  ',' ').strip()
    str3 = str2.replace(' ','_')
    return str3

def getPattern(filename):
    for page_layout in extract_pages(filename):
        k = 0
        exsitTopic = False
        articleNum = None
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                if k == 0:
                    for text_line in element:
                        for character in text_line:
                            if isinstance(character, LTChar):
                                if 'Bold' in character.fontname and character.size == 18:
                                    exsitTopic = True
                k = k + 1
                matchNum = re.findall(r"Article\sNo.:\s(\d{6})", element.get_text())
                if len(matchNum):
                    articleNum = matchNum[0]
                    break
                if k >= 3:
                    break
        if exsitTopic == True and articleNum != None:
            return('pattern1',articleNum)

tables = camelot.read_pdf(filename, pages="1", flavor='lattice')

pattern, articleNum = getPattern(filename)
print(pattern, articleNum)

# for table in tables:
#     print(table.df)


IRI = "http://example.org/engineering-info.owl"
FILE = "test7.owl"

onto = get_ontology(IRI)
with onto:
    # classes
    class product_Pilz(Thing):
        comment = ["parent class of all Pilz products"]
    class RevPi_Core_3(product_Pilz):
        pass
    class hasAttributeOf(ObjectProperty):
        domain = [RevPi_Core_3]
        range = [str]
    for table in tables:
        pd.set_option('display.max_rows', None)
        tdf = table.df
        tdf.columns = ['attr', 'value']
        product_instance = RevPi_Core_3(articleNum.replace(' ','_'))
        for index, row in tdf.iterrows():
            attrspan = processStr(row['attr'])
            attrClass = types.new_class(attrspan,(Thing,))
            value = types.new_class('valueOf'+attrspan,(DatatypeProperty,))
            value.domain.append(attrClass)
            value.range.append(str)
            relation = types.new_class('hasAttributeOf'+attrspan,(hasAttributeOf,))
            relation.domain.append(RevPi_Core_3)
            relation.range.append(attrClass)
            attr_instance = attrClass()
            getattr(attr_instance, 'valueOf'+attrspan).append(row['value'])
            getattr(product_instance, 'hasAttributeOf'+attrspan).append(attr_instance)
onto.save(file=FILE)

# def getPattern(filename):
#     for page_layout in extract_pages(filename, page_numbers=[0]):
#         # list1 = list(element  for element in page_layout if isinstance(element, LTTextContainer))
#         # print(list1[0].get_text())
#         firstElem = None
#         for element in page_layout:
#             if isinstance(element, LTTextBoxHorizontal):
#                 firstElem = element
#                 break
#         if firstElem != None:

#                 # if element.get_text().replace('\n','') == 'Accessories':
#                 #     return('pattern2')
#                 for text_line in element:
#                     # print(text_line.gettext())
#                     for character in text_line:
#                         if isinstance(character, LTChar):
#                             # if character.size > 11:
#                             #     print(character.fontname, character.size, character.get_text())
#                             if 'Bold' in character.fontname and character.size == 18:
#                                 return('pattern1')

# print(getPattern(filename))