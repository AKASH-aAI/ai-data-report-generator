def detect_datatypes(df):

    datatype_info = {}

    for column in df.columns:

        datatype_info[column] = str(df[column].dtype)

    return datatype_info 