import pandas as pd
import os
from rna.data_conversion_helper_functions.convert_quantsf_to_csv import convert_all_species_files
from rna.data_conversion_helper_functions.create_expression_matrix import create_expression_matrix
from rna.data_conversion_helper_functions.process_expression_matrix import process_expression_matrix


def process_rna_expression_data():
    """ Process raw RNA expression data to obtain median expression of each transcript."""

    # Convert raw quant.sf files (output of nf-core rna-seq pipeline) to csv files.
    raw_data_path = 'quant_files/raw'  # path to raw quant files folder
    convert_all_species_files(raw_data_path)

    # Create expression matrices of length scaled TPM values, indexed by transcript ID.
    processed_data_path = 'quant_files/processed'
    create_expression_matrix(raw_data_path, processed_data_path)

    # Process expression matrices to filter for transcript with RSD < 2 and calculate median expression
    median_expression_path = 'median_expression_files'
    process_expression_matrix(processed_data_path, median_expression_path)


def merge_datasets(species_name):
    """ Merge DNA and RNA data by transcript ID.

    Args:
        species_name (str)

    Returns:
        DataFrame: Merged DNA and RNA data for the all transcripts of the given species.
                Columns: ensembl_gene_id, transcript_id, promoter, utr5, cds, utr3, terminator sequences
                64x codon frequencies, cds_length, utr5_length, utr3_length, utr5_gc, cds_gc, utr3_gc,
                cds_wobble2_gc, cds_wobble3_gc, median_expression

        OR None if one of the DNA or RNA data paths does not exist
    """
    # Specify CSV file paths of the DNA and RNA datasets
    dna_dataset_path = f"dna/csv_files/ensembl_data_{species_name}.csv"
    rna_dataset_path = f"rna/median_expression_files/rna_expression_{species_name}.csv"  # median expression matrix

    # Check if both files exist
    if not os.path.exists(dna_dataset_path):
        print(f"Error: DNA dataset not found at {dna_dataset_path}.")
        return None
    if not os.path.exists(rna_dataset_path):
        print(f"Error: RNA dataset not found at {rna_dataset_path}.")
        return None

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
