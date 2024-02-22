import pandas as pd


def calculate_rsd(df, gene_id_column):
    # Calculate the mean and standard deviation across the row
    df['mean'] = df.iloc[:, 1:].mean(axis=1)
    df['std_dev'] = df.iloc[:, 1:-1].std(axis=1)
    # Calculate the RSD (Relative Standard Deviation)
    df['rsd'] = df['std_dev'] / df['mean']
    return df


def calculate_median_expression():
    pass


def process_expression_matrix(file_path):
    # Apply the function to the dataframe
    df_rsd = calculate_rsd(df, 'ensembl_gene_id')

    # Filter the genes with RSD < 2
    filtered_genes = df_rsd[df_rsd['rsd'] < 2]


if __name__ == "__main__":
    folder = 'quant_files/processed'
    process_expression_matrix(folder)
