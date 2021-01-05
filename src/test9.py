import camelot
from numpy.core.numeric import NaN
from pdfminer.high_level import extract_pages
from owlready2 import DatatypeProperty, FunctionalProperty, get_ontology, Inverse, \
     InverseFunctionalProperty, ObjectProperty, Thing, TransitiveProperty, SymmetricProperty,types
from pdfminer.layout import LTCurve, LTTextBoxHorizontal, LTTextContainer, LTChar, LTTextLine, LTLine
import pandas as pd
import re
from ontology_creator import OntologyCreator

def processStr(str):
    str1 = re.sub(r"\s+|,|-|/|\(|\)|:|\|", ' ',str).replace("-\n", "").replace("\n", " ")
    str2 = str1.replace('°C',' degree').replace(' x ','x').replace('  ',' ').strip()
    str3 = str2.replace(' ','_')
    return str3


filename = "../data/en/data_sheet/Pilz/S1EN_Data_Sheet_1001845-EN-01.pdf"

referenceList = []
otherList = []

labels = ['General','Electrical data','Measuring circuit','Relay outputs','Times','Environmental data','Mechanical data','Product Type','Type']
for page in extract_pages(filename):
    page_num = page.pageid
    page_width = page.width
    page_height = page.height
    # print(page_width, page_height)
    # print('               ')
    labelList =[]
    yLineList = []
    if page_num == 6 or page_num== 7:
        print('_________________________')
        print(page.pageid)
        characterSize = 8
        maxSizeList = []
        for element in page:
            if isinstance(element, LTCurve):
                if element.width > 110 and element.height < 0.2:             
                    yLineList.append(element.bbox[1])
                    # print(element.bbox[1])

        
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    label = ''
                    coorList = []
                    sizeList = []
                    for character in text_line:
                        if isinstance(character, LTChar):
                            if 'Bold' in character.fontname:
                                label = label + character.get_text()
                                # if character.matrix[-1] > y:
                                #     y = character.matrix[-1] + character.size
                                #     print(character.size)
                                coorList.append(character.matrix[-1])
                                sizeList.append(character.size)
                    if len(coorList):
                        y = sum(coorList)/len(coorList) + max(sizeList)
                    else:
                        y = None
                    if label in labels and y != None:
                        maxSizeList.append(max(sizeList))
                        labelList.append({'label':label, 'y':y})
        characterSize = sum(maxSizeList)/len(maxSizeList)
        print(characterSize)
        df_label = pd.DataFrame(labelList)

        # print(df_label)
        if not df_label.empty:
            df_label['next_y'] = df_label['y'].shift(-1)
            df_label.loc[df_label.index[-1], 'next_y'] = 60
            df_label['border'] = ""
            for row in df_label.itertuples():
                next_y = getattr(row, 'next_y')
                ascendList = sorted(list(x for x in yLineList if x>next_y))
                first_min = ascendList[0]
                second_min = ascendList[1]
                if second_min-first_min > 25:
                    df_label.at[row.Index, 'border'] = second_min
                else:
                    df_label.at[row.Index, 'border'] = first_min

            # print(df_label)
            df_label['line'] = ""
            for row in df_label.itertuples():
                # list0 = [0, getattr(row, 'y'), page_width, getattr(row, 'border')]
                # str1 = ','.join(str(y) for y in list0)
                # df_label.at[row.Index, 'region'] = str1
                # df_label.at[row.Index, 'line'] = sorted(list(x for x in yLineList if x >= getattr(row, 'border') and x <= getattr(row, 'y')),reverse=True)
                list0 = list(x for x in yLineList if x >= getattr(row, 'border') and x <= getattr(row, 'y'))
                list0.append(getattr(row, 'y'))
                yList = sorted(list0,reverse=True)
                sepList = []
                for i in range(len(yList)-1):
                    if yList[i]-yList[i+1] > characterSize * 2:
                        sepList.append(yList[i])
                        sepList.append(yList[i+1])
                sepList.append(yList[0])
                sepList.append(yList[-1])
                sepList = sorted(list(set(sepList)),reverse=True)
                print(yList)
                print(sepList)
                print('_________')

            print(df_label)

#                 regionList = []
#                 regionList.append(str1)
#                 # print(regionList)
#                 if getattr(row, 'label') != 'Product Type' and getattr(row, 'label') != 'Type':
#                     # print('1111111111')
#                     tables = camelot.read_pdf(filename, pages=str(page_num), flavor='stream', table_areas=regionList)
#                     for table in tables:
#                         otherList.append(table.df)
#                         # print(table.df)
#                 else:
#                     # print('222222222')
#                     tables = camelot.read_pdf(filename, pages=str(page_num), flavor='lattice', table_areas=regionList)
#                     if not len(tables):
#                         tables = camelot.read_pdf(filename, pages=str(page_num), flavor='stream', table_areas=regionList)
#                     for table in tables:
#                         referenceList.append(table.df)


# for x in otherList:
#     print(x)