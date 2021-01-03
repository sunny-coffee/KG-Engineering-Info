
# from typing import Text
import camelot
import pandas as pd
from PyPDF2 import PdfFileReader

# class TableExtractor:

#     __filename: str

#     def __init__(self, filename):
#         self.__filename = filename

#     def getTable(self):

#         pdf = PdfFileReader(open(self.__filename, "rb"))
#         table_page = []
#         for i in range(0, pdf.getNumPages()):
#             pageObj = pdf.getPage(i)
#             extractedText = pageObj.extractText()
#             if 'Datenblatt' in extractedText:
#                 table_page.append(i+1)
#         page_str = ','.join(str(i) for i in table_page)
#         if page_str == "":
#             return table_page
#         tables = camelot.read_pdf(self.__filename, pages=page_str, flavor='stream')
#         num = len(tables)

#         table_list = []
#         for j in range(num):
#             data = tables[j].df
#             df = pd.DataFrame(columns=['Merkmal','Wert'])
            
#             for i in range(int(data.shape[1]/2)):
#                 new_df = data.iloc[:,2*i:2*i+2]
#                 new_col = ['Merkmal','Wert']
#                 new_df.columns = new_col
                
#                 df = pd.concat([df,new_df],axis=0,ignore_index=True)
#             if df[df["Merkmal"].str.contains("Merkmal")].empty:
#                 continue

            
#             for i in range(int(df.shape[0])):
#                 if (df.loc[i,'Merkmal']=="") & (df.loc[i,'Wert']!=""):
#                     df.loc[i-1,'Wert'] = df.loc[i-1,'Wert'] + ' ' + df.loc[i,'Wert']
#                     df.drop(index=[i],inplace=True)
#                     df.rename(index={i-1: i},inplace=True)
#             # print(df[(df.Merkmal=="" | df.Wert=="")].index)
#             df.drop(df[(df['Wert']=="")].index, inplace=True)  
#             df.index = list(range(int(df.shape[0])))
#             df.drop(index = range(df[(df['Merkmal'] == 'Merkmal') & (df['Wert'] == 'Wert')].index[0]+1), inplace=True)  
#             df['Merkmal'] = df['Merkmal'].str.replace(r'[^\w\s]+', '')
#             df.index = list(range(int(df.shape[0])))
    
#             table_list.append(df)
#         return table_list

filename = "../data/en/data_sheet/Pilz/PSEN_Cable_M8-M8_8p_Data_sh_1002478-EN-04.pdf"
tables = camelot.read_pdf(filename, pages="1-end", flavor='lattice')
for table in tables:
    pd.set_option('display.max_rows', None)
    tdf = table.df
    # pd.set_option('display.max_columns', None)
    if tdf.iloc[0,0] == 'Product type' and tdf.iloc[0,-1] == 'Order no.':
        print(tdf)
        # for index, row in tdf.iterrows():
        #     print(row['attribute'] in ['Electrical data', 'Safety-related characteristic data', 'Times', 'Environmental data', 'Mechanical data'])

