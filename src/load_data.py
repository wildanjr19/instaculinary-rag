import pandas as pd
# Tambahkan ini agar VPS bisa menemukan folder src kamu
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
def load_csv(path):
    df = pd.read_csv(path)
    return df