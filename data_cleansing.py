import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


df = pd.read_csv('./vehicles.csv')
print(df.head())

filtered_df = df[(df['year'] >= 2021) & (df['year'] <= 2025)]
print(filtered_df)
filtered_df.to_csv('filtered_file.csv', index=False)