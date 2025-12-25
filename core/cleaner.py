def clean_data(df):
    df = df.drop_duplicates()
    df.columns = [c.strip().lower() for c in df.columns]
    return df
