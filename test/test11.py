import camelot

# filename = "./data/en/data_sheet/Pilz/P2HZ_X1_Data_sheet_1002151-EN-02.pdf"
# tables = camelot.read_pdf(filename, pages='8', flavor='stream', table_regions = ['0,677.9003,595.22,559.62'])
# for table in tables:
#     df = table.df
#     print(df)
    # columns = list(df.iloc[0][i] for i in range(df.shape[1]))
    
    # print(columns)

filename = "./data/en/data_sheet/Festo/VTEM_EN.PDF"
tables = camelot.read_pdf(filename, pages='14', flavor='stream')
for table in tables:
    df = table.df
    print(df)
    df.to_csv('Excel File Path.csv')