def clean_data(df, intent):

    if not intent["quality"]["clean"]:
        return df

    df = df.drop_duplicates()
    df = df.dropna()

    return df
