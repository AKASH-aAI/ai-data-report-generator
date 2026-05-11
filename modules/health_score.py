def calculate_health_score(df, outlier_report):

    total_rows = len(df)
    total_cols = len(df.columns)

    # Missing values
    missing_values = df.isnull().sum().sum()

    missing_penalty = (
        missing_values / (total_rows * total_cols)
    ) * 100 if total_rows > 0 else 0

    # Duplicate rows
    duplicate_rows = df.duplicated().sum()

    duplicate_penalty = (
        duplicate_rows / total_rows
    ) * 100 if total_rows > 0 else 0

    # Outlier penalty
    total_outliers = 0

    for v in outlier_report.values():
        if isinstance(v, list):
            total_outliers += len(v)

        elif isinstance(v, (int, float)):
            total_outliers += v

        elif isinstance(v, bool):
            total_outliers += int(v)

    outlier_penalty = (
        total_outliers / (total_rows * total_cols)
    ) * 20 if total_rows > 0 else 0

    # Final score
    score = 100 - (
        (missing_penalty * 2.5) +
        (duplicate_penalty * 3) +
        (outlier_penalty * 0.5)
    )

    score = max(0, min(100, round(score, 1)))

    return {
        "overall_score": score,
        "completeness": round(100 - missing_penalty, 1),
        "quality_score": round(
            100 - duplicate_penalty - (outlier_penalty * 0.3),
            1
        ),
        "total_missing_values": int(missing_values),
        "duplicate_rows": int(duplicate_rows),
        "total_outliers": int(total_outliers)
    }  