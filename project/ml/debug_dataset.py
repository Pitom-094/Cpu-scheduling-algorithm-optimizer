import pandas as pd
import os

data_path = r"d:\book 3-1\OS\project\dataset\cpu_dataset.csv"
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    print("Class distribution:")
    print(df['best_algo'].value_counts())
    print("\nFeature means by class:")
    print(df.groupby('best_algo').mean())
else:
    print("Dataset not found.")
