def analyze_columns(df):
    column_report= []

    for column in df.columns:
        column_info = {
            'column name':column,
            'Datatype':str(df[column].dtype),
            'Missing values':df[column].isnull().sum(),
            'Unique values':df[column].nunique()
        }
        column_report.append(column_info)
    
    return column_report 