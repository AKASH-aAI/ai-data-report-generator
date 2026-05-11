def get_dataset_summary(df):
    total_rows = df.shape[0]
    total_columns = df.shape[1]

    return {
        'Total rows':total_rows,
        'Total columns':total_columns
    }

