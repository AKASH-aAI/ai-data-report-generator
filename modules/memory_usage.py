def get_memory_usage(df):
    memory = df.memory_usage(deep=True).sum()
    memory_in_kb = memory/1024

    return f"{memory_in_kb:.2f} KB"