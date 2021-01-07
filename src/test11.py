import camelot

filename = "../data/en/data_sheet/Pilz/PSEN_Cable_M8-M8_8p_Data_sh_1002478-EN-04.pdf"
tables = camelot.read_pdf(filename, pages='7', flavor='lattice', table_regions = ['0,221.8823665728569,595.27557373,85.86601877795943'])
for table in tables:
    df = table.df
    columns = list(df.iloc[0][i] for i in range(df.shape[1]))
    
    print(columns)