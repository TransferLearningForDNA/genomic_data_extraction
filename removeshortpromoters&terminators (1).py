# -*- coding: utf-8 -*-
"""removeshortpromoters&terminators.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RotI6GX_Rr0mroUAkSxL8SEOOJegTL3G
"""

import pandas as pd
import numpy as np

# Function to calculate the RSD and filter the dataset
def filter_genes_by_rsd(expression_data, threshold=2):
    # Calculate the mean and standard deviation of expression levels across all conditions
    expression_data['mean'] = expression_data.iloc[:, 1:].mean(axis=1)
    expression_data['std_dev'] = expression_data.iloc[:, 1:-1].std(axis=1)

    # Calculate the RSD (Relative Standard Deviation) for each gene
    expression_data['rsd'] = expression_data['std_dev'] / expression_data['mean']

    # Filter the genes to keep only those with RSD < threshold
    filtered_data = expression_data[expression_data['rsd'] < threshold]

    return filtered_data

# Let 'df' be DataFrame with the mRNA expression levels (dummy data)
# Replace with the actual data loading step for original dataset
# 'df' is created with random expression levels for illustration purposes
np.random.seed(0)
dummy_data = {
    'ensembl_gene_id': [f'ENSG{str(i).zfill(11)}' for i in range(1, 11)],
    'condition_1': np.random.poisson(lam=100, size=10),
    'condition_2': np.random.poisson(lam=100, size=10),
    'condition_3': np.random.poisson(lam=100, size=10),
    'condition_4': np.random.poisson(lam=100, size=10),
    'condition_5': np.random.poisson(lam=100, size=10),
}
df = pd.DataFrame(dummy_data)

# Apply the function to calculate RSD and filter the dataset
filtered_genes = filter_genes_by_rsd(df)

# Display the filtered dataset
filtered_genes
