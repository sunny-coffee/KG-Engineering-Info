import camelot
from numpy.core.numeric import NaN
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextContainer, LTChar, LTTextLine
import pandas as pd

filename = "../data/en/data_sheet/Pilz/PDP67_F_4_code_Data_sheet_1002222-EN-05.pdf"


labels = ['General','Electrical data','Measuring circuit','Relay outputs','Times','Environmental data','Mechanical data','Order reference']
for page in extract_pages(filename):
    print('_________________________')
    # print(pagenumber)
    page_num = page.pageid
    page_width = page.bbox[2]
    page_height = page.bbox[3]
    # print(page_height)
    print('               ')
    labelList =[]
    for element in page:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                stri = ''
                y = 0
                for character in text_line:
                    if isinstance(character, LTChar):
                        if 'Bold' in character.fontname:
                            stri = stri + character.get_text()
                            if character.matrix[-1] > y:
                                y = character.matrix[-1]
                if stri in labels:
                    labelList.append({'label':stri, 'y':y})
    df_label = pd.DataFrame(labelList)
    
    if not df_label.empty:
        
        df_label['next_y'] = df_label['y'].shift(-1)
        df_label['region'] = ""
        df_label.loc[df_label.index[-1], 'next_y'] = 0
        for row in df_label.itertuples():
            # df_label.at[row.Index, 'region'] = 'ssss'
            # print(getattr(row, 'y'))
            list0 = [0, getattr(row, 'y'), page_width, getattr(row, 'next_y')]
            str1 = ','.join(str(y) for y in list0)
            # print(str1)
            regionList = []
            regionList.append(str1)
            print(regionList)
            
        # print(df_label)
        # print(regionList)

            tables = camelot.read_pdf(filename, pages=str(page_num), flavor='stream', table_areas=regionList)
            for table in tables:
                # df1 = table.df
                # if df1.shape[1] == 2: 
                print(table.df)