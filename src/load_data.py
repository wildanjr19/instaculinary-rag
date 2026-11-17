import pandas as pd

def load_csv(path):
    df = pd.read_csv(path, dtype={"id": "string"})
    return df
