import camelot
import pandas as pd

class TableExtractor:

    __filename: str

    def __init__(self, filename):
        self.__filename = filename

    def getTable(self):
        tables = camelot.read_pdf(self.__filename, pages='1-end', flavor='stream')
        num = len(tables)

        table_list = []
        for j in range(num):
            data = tables[j].df
            df = pd.DataFrame(columns=['characteristic','value'])

            for i in range(int(data.shape[1]/2)):
                new_df = data.iloc[:,2*i:2*i+2]
                new_col = ['characteristic','value']
                new_df.columns = new_col
                
                df = pd.concat([df,new_df],axis=0,ignore_index=True)

            for i in range(int(df.shape[0])):
                if (df.loc[i,'characteristic']=="") & (df.loc[i,'value']!=""):
                    df.loc[i-1,'value'] = df.loc[i-1,'value'] + ' ' + df.loc[i,'value']
                    df.drop(index=[i],inplace=True)
                    df.rename(index={i-1: i},inplace=True)
                    
            df.index = list(range(int(df.shape[0])))
            df['characteristic'] = df['characteristic'].str.replace(r'[^\w\s]+', '')
            table_list.append(df)
        return table_list

