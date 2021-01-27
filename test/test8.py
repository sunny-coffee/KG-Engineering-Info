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
    # print('_________________________')
    # print(page.pageid)
    page_num = page.pageid
    page_width = page.width
    page_height = page.height
    # print(page_width, page_height)
    # print('               ')
    labelList =[]
    yLineList = []
    
    for element in page:
        if isinstance(element, LTCurve):
            if element.width > 120 and element.height < 0.2:             
                yLineList.append(element.bbox[1])
                # print(element.bbox[1])

    
        if isinstance(element, LTTextContainer):
            for text_line in element:
                label = ''
                y = 0
                for character in text_line:
                    if isinstance(character, LTChar):
                        if 'Bold' in character.fontname:
                            label = label + character.get_text()
                            if character.matrix[-1] > y:
                                y = character.matrix[-1] + character.size
                if label in labels:
                    labelList.append({'label':label, 'y':y})
    df_label = pd.DataFrame(labelList)

    
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
                df_label.at[row.Index, 'border'] = second_min + 2.5
            else:
                df_label.at[row.Index, 'border'] = first_min + 2.5

        # print(df_label)
        for row in df_label.itertuples():
            list0 = [0, getattr(row, 'y'), page_width, getattr(row, 'border')]
            str1 = ','.join(str(y) for y in list0)
            # df_label.at[row.Index, 'region'] = str1

        # print(df_label)

            regionList = []
            regionList.append(str1)
            # print(regionList)
            if getattr(row, 'label') != 'Product Type' and getattr(row, 'label') != 'Type':
                # print('1111111111')
                tables = camelot.read_pdf(filename, pages=str(page_num), flavor='stream', table_areas=regionList)
                for table in tables:
                    otherList.append(table.df)
                    # print(table.df)
            else:
                # print('222222222')
                tables = camelot.read_pdf(filename, pages=str(page_num), flavor='lattice', table_areas=regionList)
                if not len(tables):
                    tables = camelot.read_pdf(filename, pages=str(page_num), flavor='stream', table_areas=regionList)
                for table in tables:
                    referenceList.append(table.df)
                    # print(table.df)

# for df in referenceList:
#     print(df)

# IRI = "http://example.org/engineering-info.owl"
# FILE = "test6.owl"


# ontologyCreator1 = OntologyCreator(IRI,FILE)
# ontologyCreator1.add_from_referenceList(referenceList) 
# onto = get_ontology(IRI)
# with onto:
#     # classes
#     class product_Pilz(Thing):
#         comment = ["parent class of all Pilz products"]
#     class S1EN(product_Pilz):
#         pass
#     class hasAttributeOf(ObjectProperty):
#         domain = [S1EN]
#         range = [str]

#     for tdf in referenceList:
#         attrList = list(tdf.iloc[0,i] for i in range(tdf.shape[1]))
#         if ('Product type' in attrList or 'Type' in attrList) and 'Order no.' in attrList:
#             tdf.columns = attrList
#             tdf.drop(index=[0], inplace=True)
#             # print(tdf)
#             for attr in attrList:
#                 if len(attr):                   
#                     attrspan = processStr(attr)
#                     attrSuperClass = types.new_class(attrspan,(Thing,))
#                     attrClass = types.new_class(attrspan+'OfS1EN',(attrSuperClass,))
#                     value = types.new_class('valueOf'+attrspan,(DatatypeProperty,))
#                     value.domain.append(attrClass)
#                     value.range.append(str)
#                     relation = types.new_class('hasAttributeOf'+attrspan,(hasAttributeOf,))
#                     relation.domain.append(S1EN)
#                     relation.range.append(attrClass)
#             for index, row in tdf.iterrows():
#                 product_instance = S1EN(processStr(row['Order no.']))
#                 for attr in attrList:
#                     if len(attr):
#                         if len(row[attr]):
#                             attrspan = processStr(attr)
#                             attr_instance = getattr(onto, attrspan+'OfS1EN')()
#                             getattr(attr_instance, 'valueOf'+attrspan).append(row[attr])
#                             getattr(product_instance, 'hasAttributeOf'+attrspan).append(attr_instance)
# onto.save(file=FILE)

for df in otherList:

    if df.shape[1] == 2:
        print(df)
        print('___________________')
        superclass = df.iloc[0,0]
        if superclass not in labels:
            break
        else:
            df.columns = ['attr', 'value']
            inNumSpan = df.iloc[0,1]
            matchList = re.findall(r"\d\d\d_\d\d\d",processStr(inNumSpan))
            if len(matchList) != 1:
                df.drop(index=[0], inplace=True)
                last_value = None
                last_row = None
                for row in df.itertuples():
                    if not len(getattr(row,'attr')) and last_row != None:
                        # print(getattr(last_row,'value') + ' ' + getattr(row,'value'))
                        df.at[last_row.Index, 'value'] = last_value + ' ' + getattr(row,'value')
                        last_value = last_value + ' ' + getattr(row,'value')
                        df.drop(index=[row.Index], inplace=True)
                    else:
                        last_value = getattr(row,'value')
                        last_row = row
                for row in df.itertuples():
                    if not len(getattr(row,'value')) and re.match('^[a-z]+$',getattr(row,'attr')):
                        # print(getattr(last_row,'value') + ' ' + getattr(row,'value'))
                        df.at[last_row.Index, 'value'] = last_value + ' ' + getattr(row,'value')
                        last_value = last_value + ' ' + getattr(row,'value')
                        df.drop(index=[row.Index], inplace=True)
                    else:
                        last_value = getattr(row,'value')
                        last_row = row
            else:
                inNum = matchList[0]


        print(df)
        print('___________________')
    elif df.shape[1] >= 3:
        isTrue = True
        attrList = list(df.iloc[0,i] for i in range(df.shape[1]))
        for index, attr in enumerate(attrList):
            if index == 0:
                if len(attr):
                    superclass = processStr(attr)
                else:
                    isTrue = False
                    break
            else:
                matchList = re.findall(r"\d\d\d_\d\d\d",processStr(attr))
                if len(matchList) != 1:
                    isTrue = False
                    break
        if isTrue:
            print(df)