import pandas as pd


def merge_datasets(species_name):
    """ Merge DNA and RNA data by gene ID.

    Args:
        species_name (str)
    """
    # Specify CSV file paths of the DNA and RNA datasets
    dna_dataset_path = f"dna/csv_files/ensembl_data_{species_name}.csv"
    rna_dataset_path = f"rna/quant_files/processed/{species_name}.csv"  # median expression matrix

    # Read datasets into pandas DataFrames
    dna_df = pd.read_csv(dna_dataset_path)
    rna_df = pd.read_csv(rna_dataset_path)

    # Merge datasets based on transcript ID
    merged_df = pd.merge(dna_df, rna_df, on='transcript_id', how='inner')

    # Save merged dataframe to csv
    merged_df.to_csv(f'merged_csv_files/merged_{species_name}_data.csv', index=False)

    return merged_df


if __name__ == "__main__":
    merge_datasets(species_name='homo_sapiens')
