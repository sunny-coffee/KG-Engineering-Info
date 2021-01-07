import camelot
from numpy.core.numeric import NaN
from owlready2.util import FirstList
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


filename = "../data/en/data_sheet/Pilz/PSEN_Cable_M8-M8_8p_Data_sh_1002478-EN-04.pdf"

referenceList = []
otherList = []
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
labels = ['General','Electrical data','Measuring circuit','Relay outputs','Times','Environmental data','Mechanical data','Product type','Type']



for page in extract_pages(filename):
    page_num = page.pageid
    page_width = page.width
    page_height = page.height
    # print(page_width, page_height)
    # print('               ')
    labelList =[]
    y_dict = {}

    print('_________________________')
    print(page.pageid)
    characterSize = 8
    maxSizeList = []
    for element in page:
        if isinstance(element, LTCurve):
            # if page_num == 7:
            #     print(element.bbox[1],element.width,element.height)
            # if element.width > 110 and element.height < 0.2:             
            #     yLineList.append(element.bbox[1])
                # print(element.bbox[1])

            if element.height < 0.5:
                if not element.bbox[1] in y_dict:
                    y_dict[element.bbox[1]] = element.width
                else:
                    y_dict[element.bbox[1]] =  y_dict[element.bbox[1]] + element.width
    # if page_num == 7:
    #     print(yLineList)

    
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
    yLineList = [k for k,v in y_dict.items() if v>400 ]
    if len(maxSizeList):
        characterSize = sum(maxSizeList)/len(maxSizeList)
    # print(characterSize)
    df_label = pd.DataFrame(labelList)

    # if page_num == 7:
    #         print(yLineList)

    # print(df_label)
    if not df_label.empty:
        df_label['next_y'] = df_label['y'].shift(-1)
        df_label.loc[df_label.index[-1], 'next_y'] = 60
        df_label['border'] = ""
        for row in df_label.itertuples():
            next_y = getattr(row, 'next_y')
            y = getattr(row, 'y')
            ascendList = sorted(list(x for x in yLineList if x>next_y and x < y))
            if len(ascendList) == 0:
                df_label.drop(index=[row.Index], inplace=True)
            elif len(ascendList) == 1:
                df_label.at[row.Index, 'border'] = ascendList[0]
            else:
                first_min = ascendList[0]
                second_min = ascendList[1]
                if second_min-first_min > 25:
                    df_label.at[row.Index, 'border'] = second_min
                else:
                    df_label.at[row.Index, 'border'] = first_min
        # if page_num == 7:
        #     print(df_label)
        df_label['sub_regions'] = ""
        df_label['region'] = ""
        for row in df_label.itertuples():
            
            # df_label.at[row.Index, 'line'] = sorted(list(x for x in yLineList if x >= getattr(row, 'border') and x <= getattr(row, 'y')),reverse=True)
            list0 = list(x for x in yLineList if x > getattr(row, 'border') and x < getattr(row, 'y'))
            list0.append(getattr(row, 'y'))
            list0.append(getattr(row, 'border'))
            # if getattr(row, 'label') == 'Product type':
            #     print(list0)
            yList = sorted(list0,reverse=True)
            sepList = []
            for i in range(len(yList)-1):
                if yList[i]-yList[i+1] > characterSize * 2:
                    sepList.append(yList[i])
                    sepList.append(yList[i+1])
            sepList.append(yList[0])
            sepList.append(yList[-1])
            sepList = sorted(list(set(sepList)),reverse=True)
            # if getattr(row, 'label') == 'Product type':
            #     print(yList)
            # if getattr(row, 'label') == 'Product type':
            #     print(sepList)
            regionList = []
            for i in range(len(sepList)-1):
                list1 = [0, sepList[i], page_width, sepList[i+1]+2.5]
                str1 = ','.join(str(y) for y in list1)
                # print(str1)
                regionList.append(str1)
            # if page_num == 7:
            #     print(regionList)
            df_label.at[row.Index, 'sub_regions'] = regionList
            list2 = [0, getattr(row, 'y'), page_width, getattr(row, 'border')+2.5]
            str2 = ','.join(str(y) for y in list2)
            df_label.at[row.Index, 'region'] = [str2]
            
            if True:
                tables = camelot.read_pdf(filename, pages=str(page_num), flavor='stream', table_areas=regionList)
                firstDF = tables[0].df
                # print(firstDF)
                # print(all(list(type(x)==int for x in range(2,firstDF.shape[1]))))
                frames = []
                if firstDF.shape[1] > 2 and firstDF.iloc[0,0] in labels and all(list(type(x)==int for x in range(1,firstDF.shape[1]))):
                    attrList = list(firstDF.iloc[0,i] for i in range(firstDF.shape[1]))
                    valueList = attrList[1:]
                    attr = attrList[0]
                    for index, table in enumerate(tables):
                        df = table.df
                        # print(df)
                        
                        if index == 0:
                            df.drop(index=[index], inplace=True)
                        if df.shape[1] == firstDF.shape[1]:
                            df.columns = attrList
                            for i in reversed(range(len(df))):
                                if len(df.iloc[i][attr]) == 0:
                                    for value in valueList:
                                        df.iloc[i-1][value] = df.iloc[i-1][value] + ' ' + df.iloc[i][value]
                                    df.drop(index=[i], inplace=True)

                            for i in reversed(range(len(df))):
                                if any(list(len(df.iloc[i][value]) == 0 for value in valueList)):
                                    if all(list(len(df.iloc[i][value]) == 0 for value in valueList)):
                                        if i == len(df) - 1:
                                            df.iloc[i-1][attr] = df.iloc[i-1][attr] + ' ' + df.iloc[i][attr]
                                            df.drop(index=[i], inplace=True)
                                        else:
                                            for j in range(i+1, len(df)):
                                                df.iloc[j][attr] = df.iloc[i][attr] + ' ' + df.iloc[j][attr]
                                            df.drop(index=[i], inplace=True)  
                                    else:
                                        for value in attrList:
                                            df.iloc[i-1][value] = df.iloc[i-1][value] + ' ' + df.iloc[i][value]
                                        df.drop(index=[i], inplace=True)                                   
                            # print(df)
                            frames.append(df)
                result = pd.concat(frames)
                # print(result)
                otherList.append(result)

                # tableSizeList = list(table.df.shape[1] for table in tables)
                # firstDF = tables[0].df
                # frames = []
                # if firstDF.shape == (1,1) or (firstDF.shape[1] == 2 and len(firstDF.iloc[0,1]) == 0):
                #     for index, table in enumerate(tables):
                #         df = table.df
                #         if index == 0:
                #             df.drop(index=[index], inplace=True)
                #         if df.shape[1] == 2:
                #             last_value = None
                #             last_row = None
                #             # attrList = list(df.iloc[0,i] for i in range(df.shape[1]))
                #             df.columns = ['attr', 'value']
                #             for row in df.itertuples():
                #                 if not len(getattr(row,'attr')) and last_row != None:
                #                     # print(getattr(last_row,'value') + ' ' + getattr(row,'value'))
                #                     df.at[last_row.Index, 'value'] = last_value + ' ' + getattr(row,'value')
                #                     last_value = last_value + ' ' + getattr(row,'value')
                #                     df.drop(index=[row.Index], inplace=True)
                #                 else:
                #                     last_value = getattr(row,'value')
                #                     last_row = row

                #             for i in reversed(range(len(df))):
                #                 if len(df.iloc[i]['value']) == 0:
                #                     if i == len(df) - 1:
                #                         df.iloc[i-1]['attr'] = df.iloc[i-1]['attr'] + ' ' + df.iloc[i]['attr']
                #                         df.drop(index=[i], inplace=True)
                #                     else:
                #                         for j in range(i+1, len(df)):
                #                             df.iloc[j]['attr'] = df.iloc[i]['attr'] + ' ' + df.iloc[j]['attr']
                #                         df.drop(index=[i], inplace=True)
                #             frames.append(df)
                # result = pd.concat(frames)
                # otherList.append(result)
                    
            else:
                # print('222222222')
                tables = camelot.read_pdf(filename, pages=str(page_num), flavor='lattice', table_areas=regionList)
                if not len(tables):
                    tables = camelot.read_pdf(filename, pages=str(page_num), flavor='stream', table_areas=regionList)
                for table in tables:
                    referenceList.append(table.df)
        print(df_label)

# for x in otherList:
#     print(x)
# print(len(otherList))
    # for index, row in x.iterrows():
    #     print(row['attr'])
# for x in otherList:
#     print(x)