import pandas as pd

def load_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    df = df.dropna(subset=['Wellbore name'])
    numeric_cols = ['Oil', 'Water', 'Gas']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df
