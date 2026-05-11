def generate_statistics(df):

    numeric_df = df.select_dtypes(include=['int64','float64'])

    statistics = {}

    for column in numeric_df.columns:

        statistics[column] = {
            "Mean": numeric_df[column].mean(),
            "Median": numeric_df[column].median(),
            "Minimum": numeric_df[column].min(),
            "Maximum": numeric_df[column].max()
        }

    return statistics