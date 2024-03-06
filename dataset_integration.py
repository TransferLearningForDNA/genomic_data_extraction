import pandas as pd


def merge_datasets(species_name):
    """ Merge DNA and RNA data by transcript ID.

    Args:
        species_name (str)

    Returns:
        DataFrame: Merged DNA and RNA data for the all transcripts of the given species.
                Columns: ensembl_gene_id, transcript_id, promoter, utr5, cds, utr3, terminator sequences
                64x codon frequencies, cds_length, utr5_length, utr3_length, utr5_gc, cds_gc, utr3_gc,
                cds_wobble2_gc, cds_wobble3_gc, median_expression
    """
    # Specify CSV file paths of the DNA and RNA datasets
    dna_dataset_path = f"dna/csv_files/ensembl_data_{species_name}.csv"
    rna_dataset_path = f"rna/median_expression_files/rna_expression_{species_name}.csv"  # median expression matrix

    # Read datasets into pandas DataFrames
    dna_df = pd.read_csv(dna_dataset_path)
    rna_df = pd.read_csv(rna_dataset_path)

    # Merge datasets based on transcript ID
    merged_df = pd.merge(dna_df, rna_df, on='transcript_id', how='inner')

    # Save merged dataframe to csv
    merged_df.to_csv(f'merged_csv_files/merged_{species_name}_data.csv', index=False)

    print(f"Successfully merged DNA and RNA data for species {species_name}!")

    return merged_df


if __name__ == "__main__":
    merge_datasets(species_name='chlamydomonas_reinhardtii')
