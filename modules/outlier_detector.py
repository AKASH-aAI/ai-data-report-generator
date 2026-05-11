def detect_outliers(df):
    outlier_report = {}
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    for column in numeric_columns:

        clean_data = df[column].dropna()

        if len(clean_data) == 0:
            outlier_report[column] = 0
            continue

        q1 = clean_data.quantile(0.25)
        q3 = clean_data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = clean_data[
            (clean_data < lower_bound) |
            (clean_data > upper_bound)
        ]
        outlier_report[column] = len(outliers)
    return outlier_report 