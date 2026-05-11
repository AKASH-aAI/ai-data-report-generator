def check_duplicates(df):
    duplicate_rows = df.duplicated().sum()
    return duplicate_rows