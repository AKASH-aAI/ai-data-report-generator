def check_missing_values(df):
    missing_values = df.isnull().sum()
    return missing_values 