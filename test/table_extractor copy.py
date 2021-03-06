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
import spacy
from tree_extractor import Tree

def processStr(str):
    str1 = re.sub(r"\s+|,|-|/|\(|\)|:|\||\n", ' ',str.replace("-\n", "").replace("- ", ""))
    str2 = str1.replace('°C',' degree').replace(' x ','x').replace('  ',' ').strip()
    str3 = str2.replace(' ','_')
    return str3

class TableExtractor:

    def __init__(self, filename):
        self.filename = filename
        self.referenceList = []
        self.otherList = []
        # pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
        self.labels = ['General','Electrical data','Measuring circuit','Relay outputs','Times','Environmental data','Mechanical data', 'Safety-related characteristic data','Product type','Type']

    def extractStream(self,filename, page_num, regionList, extractType='other'):
        tables = []
        nlp = spacy.load('en_core_web_md')
        for region in regionList:
            try:
                table = camelot.read_pdf(filename, pages=str(page_num), flavor='stream', table_areas=[region])
                tables.append(table[0])
            except BaseException:
                pass
        # for table in tables:
        #     print(table.df)
        firstDF = tables[0].df
        frames = []
        if firstDF.shape[1] > 2 and firstDF.iloc[0,0] in self.labels and all(list(type(x)==int for x in range(1,firstDF.shape[1]))):
            attrList = list(firstDF.iloc[0,i] for i in range(firstDF.shape[1]))
            for index, table in enumerate(tables):
                df = table.df
                if index == 0:
                    df.drop(index=[index], inplace=True)
                    df.reset_index(drop=True, inplace=True)
                if df.shape[1] == firstDF.shape[1]:
                    df.columns = attrList
                    if extractType == 'reference':
                        # print((df.columns[2]))
                        for a in attrList:
                            if not len(a):
                                df.drop([a], axis=1, inplace=True)
                                attrList.remove(a)
                        # print(df)
                    valueList = attrList[1:]
                    attr = attrList[0]
                    for i in reversed(range(len(df))):
                        if i!=0 and len(df.iloc[i][attr]) == 0:
                            for value in valueList:
                                df.iloc[i-1][value] = df.iloc[i-1][value] + ' ' + df.iloc[i][value]
                            df.drop(index=[i], inplace=True)
                    # df.reset_index(drop=True, inplace=True)
                    # for i in reversed(range(len(df))):
                        elif i!=0 and df.iloc[i][attr][0].islower() and not(all(list(len(df.iloc[i-1][value]) == 0 for value in valueList))and not any(list(len(df.iloc[i][value]) == 0 for value in valueList))):
                            for value in attrList:
                                df.iloc[i-1][value] = df.iloc[i-1][value] + ' ' + df.iloc[i][value]
                            df.drop(index=[i], inplace=True)
                        else:
                            if any(list(len(df.iloc[i][value]) == 0 for value in valueList)):
                                if all(list(len(df.iloc[i][value]) == 0 for value in valueList)):
                                    if i == len(df) - 1:
                                        df.iloc[i-1][attr] = df.iloc[i-1][attr] + ' ' + df.iloc[i][attr]
                                        df.drop(index=[i], inplace=True)
                                    else:
                                        # next_len = len(df.iloc[i+1][attr])
                                        for j in range(i+1, len(df)):
                                            # attr_len = len(df.iloc[j][attr])
                                            # if abs((attr_len - next_len)/next_len) < 0.2:
                                            #     print('!!!!!!!!!!!!!!!!')
                                            #     print(abs((attr_len - next_len)/next_len))
                                            #     print(df.iloc[i+1][attr])
                                            #     print(df.iloc[j][attr])
                                            df.iloc[j][attr] = df.iloc[i][attr] + ' ' + df.iloc[j][attr]
                                        df.drop(index=[i], inplace=True)  
                                else:
                                    # print(i)
                                    # print(df.iloc[i])
                                    # print(df)
                                    if extractType == 'other':
                                        for value in attrList:
                                            df.iloc[i-1][value] = df.iloc[i-1][value] + ' ' + df.iloc[i][value]
                                    df.drop(index=[i], inplace=True)                                   
                    # print(df)
                    frames.append(df)
        elif firstDF.shape == (1,1) or (firstDF.shape[1] == 2 and (len(firstDF.iloc[0,1]) == 0 or type(firstDF.iloc[0,1])==int)):
            if firstDF.shape == (1,1):
                attrList = [firstDF.iloc[0,0], 'value']
            else:
                if len(firstDF.iloc[0,1]):
                    attrList = [firstDF.iloc[0,0], firstDF.iloc[0,1]]
                else:
                    attrList = [firstDF.iloc[0,0], 'value']
            for index, table in enumerate(tables):
                df = table.df
                # print(df)
                if index == 0:
                    df.drop(index=[index], inplace=True)
                if df.shape[1] == 2:
                    df.columns = attrList
                    attr = attrList[0]
                    value = attrList[1]

                    for i in reversed(range(len(df))):
                        if len(df.iloc[i][attr]) == 0:
                            df.iloc[i-1][value] = df.iloc[i-1][value] + ' ' + df.iloc[i][value]
                            df.drop(index=[i], inplace=True)
                    # df.reset_index(drop=True, inplace=True)
                    # for i in reversed(range(len(df))):
                            
                        elif i!=0 and (df.iloc[i][attr][0].islower() or df.iloc[i][attr][0:2] == 'EN') and not(len(df.iloc[i-1][value]) == 0 and len(df.iloc[i][value]) != 0 ):
                            attr1 = nlp(df.iloc[i-1][attr])
                            attr2 = nlp(df.iloc[i][attr])
                            attr_sim = attr1.similarity(attr2)
                            if len(df.iloc[i-1][value]) != 0 and len(df.iloc[i][value]) != 0:
                                value1 = nlp(df.iloc[i-1][value])
                                value2 = nlp(df.iloc[i][value])
                                val_sim = value1.similarity(value2)
                            else:
                                val_sim = 0
                            # print(attr1, attr2)
                            # print(max([attr_sim, val_sim]))
                            if max([attr_sim, val_sim]) < 0.8:
                                
                                for value in attrList:
                                    df.iloc[i-1][value] = df.iloc[i-1][value] + ' ' + df.iloc[i][value]
                                df.drop(index=[i], inplace=True)
                        elif len(df.iloc[i][value]) == 0 and  i == len(df) - 1:
                            df.iloc[i-1][attr] = df.iloc[i-1][attr] + ' ' + df.iloc[i][attr]
                            df.drop(index=[i], inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    
                    parList = []
                    # childList = []
                    treeList = []
                    parentTree = None  
                    for index, row in df.iterrows():
                        tree = Tree(index)
                        treeList.append(tree)
                        if len(row[value]) == 0:
                            parentTree = tree
                            if len(parList):
                                if parList[-1].key == index - 1:
                                    parList[-1].insertChild(parentTree)
                            parList.append(parentTree)
                        else:
                            if parentTree != None:
                                child = tree
                                parentTree.insertChild(child)
                                # childList.append(child)
                        
                    if len(parList) >= 2 and any(list(par.parent == None for par in parList[1:])):
                        for i in range(1,len(parList)):
                            childNum = len(parList[i].childs)
                            isInserted = False
                            for par in parList[0:i]:
                                if len(par.childs) == childNum:
                                    # nlp(df.iloc[parList[i].childs[j]][attr]).similarity(nlp(df.iloc[par.childs[j]][attr])
                                    min_sim =  min(list(nlp(df.iloc[parList[i].childs[j].key][attr]).similarity(nlp(df.iloc[par.childs[j].key][attr])) for j in range(childNum)))
                                    if min_sim > 0.85:
                                        isInserted = TrueisInserted = True
                                        if par.parent != None:
                                            par.parent.insertChild(parList[i])

                            if isInserted == False:
                                if parList[i].parent == None:
                                    doc1 = nlp(df.iloc[parList[i].key][attr])
                                    max_j = 0
                                    max_sim = 0
                                    for j in range(0, parList[i].key):
                                        doc2 = nlp(df.iloc[j][attr])
                                        sim = doc1.similarity(doc2)
                                        if sim > max_sim:
                                            max_j = j
                                            max_sim = sim
                                    if max_sim > 0.7:
                                        # print('!!!!!!!')
                                        # print(df.iloc[treeList[max_j].key][attr])
                                        # print(df.iloc[parList[i].key][attr])
                                        if treeList[max_j].parent != None:
                                            treeList[max_j].parent.insertChild(parList[i])

                    for item in treeList:
                        if item  not in parList:
                            iterItem = item
                            # print('--------------')
                            while True:
                                if iterItem.parent != None:
                                    # print( iterItem.parent.key, df.iloc[iterItem.parent.key][attr], '|||||', item.key,df.iloc[item.key][attr])
                                    df.iloc[item.key][attr] = df.iloc[iterItem.parent.key][attr] + '_' + df.iloc[item.key][attr]
                                    iterItem = iterItem.getParent()
                                else:
                                    break
                    
                    df.drop(index=list(par.key for par in parList), inplace=True)
                    frames.append(df)
        result = pd.concat(frames)
        result.reset_index(drop=True, inplace=True)
        return result

    def extractLattice(self, filename, page_num, regionList):
        tables = camelot.read_pdf(filename, pages=str(page_num), flavor='lattice', table_regions=regionList)
        if len(tables) != 1:
            return None
        else:
            df = tables[0].df
            columns = list(df.iloc[0][i] for i in range(df.shape[1]))
            if ('Product type' in columns or 'Type' in columns) and ('Order no.' in columns or 'no.' in columns):
                return df
            else:
                return None
    
    def getTable(self):
        for page in extract_pages(self.filename):
            page_num = page.pageid
            # if page_num != 11:
            #     continue
            page_width = page.width
            page_height = page.height
            labelList =[]
            y_dict = {}
            # print('_________________________')
            # print(page.pageid)
            characterSize = 8
            maxSizeList = []
            for element in page:
                if isinstance(element, LTCurve):
                    if element.height < 2:
                        if not element.bbox[1] in y_dict:
                            y_dict[element.bbox[1]] = element.width
                        else:
                            y_dict[element.bbox[1]] =  y_dict[element.bbox[1]] + element.width
        
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        label = ''
                        coorList = []
                        sizeList = []
                        for character in text_line:
                            if isinstance(character, LTChar):
                                if 'Bold' in character.fontname:
                                    label = label + character.get_text()
                                    coorList.append(character.matrix[-1])
                                    sizeList.append(character.size)
                        if len(coorList):
                            y = sum(coorList)/len(coorList) + max(sizeList)
                        else:
                            y = None
                        # print(label)
                        if any(sep in label for sep in self.labels)and y != None:
                            maxSizeList.append(max(sizeList))
                            labelList.append({'label':label, 'y':y})
            yLineList = [k for k,v in y_dict.items() if v>400 ]
            # print(yLineList)
            if len(maxSizeList):
                characterSize = sum(maxSizeList)/len(maxSizeList)
            df_label = pd.DataFrame(labelList)
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
                        if second_min-first_min > 60:
                            df_label.at[row.Index, 'border'] = second_min
                        else:
                            df_label.at[row.Index, 'border'] = first_min

                df_label['sub_regions'] = ""
                df_label['region'] = ""
                for row in df_label.itertuples():
                    
                    list0 = list(x for x in yLineList if x > getattr(row, 'border') and x < getattr(row, 'y'))
                    list0.append(getattr(row, 'y'))
                    list0.append(getattr(row, 'border'))
                    yList = sorted(list0,reverse=True)
                    sepList = []
                    for i in range(len(yList)-1):
                        if yList[i]-yList[i+1] > characterSize * 2:
                            sepList.append(yList[i])
                            sepList.append(yList[i+1])
                    sepList.append(yList[0])
                    sepList.append(yList[-1])
                    sepList = sorted(list(set(sepList)),reverse=True)
                    # print(sepList)
                    for i in range(len(sepList)-1):
                        if sepList[i] - sepList[i+1] < characterSize:
                            sepList.pop(i+1)

                    regionList = []
                    for i in range(len(sepList)-1):
                        list1 = [0, sepList[i], page_width, sepList[i+1]+2.5]
                        str1 = ','.join(str(y) for y in list1)
                        regionList.append(str1)
                    # print(regionList)
                    df_label.at[row.Index, 'sub_regions'] = regionList
                    list2 = [0, getattr(row, 'y'), page_width, getattr(row, 'border')+2.5]
                    str2 = ','.join(str(y) for y in list2)
                    df_label.at[row.Index, 'region'] = [str2]

                # print(df_label)
                for row in  df_label.itertuples():
                    if getattr(row, 'label') != 'Product type' and getattr(row, 'label') != 'Type':
                        # print(getattr(row, 'sub_regions'))
                        result = self.extractStream(self.filename, page_num, getattr(row, 'sub_regions'))
                        if len(result):
                            self.otherList.append(result)
                            # print(result)                  
                    else:
                        resLattice = self.extractLattice(self.filename, page_num, getattr(row, 'region'))
                        if resLattice != None:
                            if len(resLattice):
                                self.referenceList.append(resLattice)
                                # print(resLattice)
                        else:
                            result = self.extractStream(self.filename, page_num, getattr(row, 'sub_regions'), 'reference')
                            if len(result):
                                self.referenceList.append(result)
        return self.otherList, self.referenceList

filename = "../data/en/data_sheet/Pilz/P2HZ_X1_Data_sheet_1002151-EN-02.pdf"

tableExtactor1 = TableExtractor(filename)
otherList , referenceList = tableExtactor1.getTable()
for x in otherList:
    print(x)
    for index, row in x.iterrows():
        print(row[0], row[1])
print('__________________________')
for x in referenceList:
    print(x)

IRI = "http://example.org/engineering-info.owl"
FILE = "test.owl"
# FILE = "test.owl"

ontologyCreator1 = OntologyCreator(IRI,FILE)
instances = ontologyCreator1.add_from_referenceList(referenceList)
ontologyCreator1.add_from_otherList(otherList, instances)
