import os
import pandas as pd


def get_length_scaled_tpm_matrix(counts_mat: pd.DataFrame, abundance_mat: pd.DataFrame, length_mat: pd.DataFrame) \
        -> pd.DataFrame:
    """ Generate length scaled TPM matrix.

    Args:
        counts_mat (DataFrame): A matrix of original counts (NumReads).
        abundance_mat (DataFrame): A matrix of abundances (TPM).
        length_mat (DataFrame): A matrix of effective lengths.

    Returns:
        DataFrame: A matrix of length scaled TPM values indexed by transcript ID.
    """

    # Calculate the sum of counts across all transcripts for each sample: per-sample library size
    counts_sum = counts_mat.sum(axis=0)

    # Calculate the average transcript lengths (averaged over samples)
    length_means = length_mat.mean(axis=1)

    # Multiply abundance matrix (TPM) by average transcript lengths
    length_tpm_mat = abundance_mat.multiply(length_means, axis=0)

    # Calculate the sum of new counts across transcripts for each sample
    new_sum = length_tpm_mat.sum(axis=0)

    # Determine the scaling factor for each sample
    scaling_factor = counts_sum / new_sum

    # Apply the scaling factor to scale new counts to match the original total counts
    length_scaled_tpm_mat = length_tpm_mat.multiply(scaling_factor, axis=1)

    return length_scaled_tpm_mat


def create_expression_matrix(raw_data_path: str, processed_data_path: str) -> None:
    """ Create the expression matrices for all species.

    Args:
        raw_data_path (str): Path to the folder containing raw quant files.
        processed_data_path (str): Path to store the processed expression matrix csv files.
    """

    # Iterate over species
    for species in os.listdir(raw_data_path):
        raw_csv_data_path = os.path.join(raw_data_path, species, 'csv_files')

        # Skip if it's not a directory (e.g., .DS_Store)
        if not os.path.isdir(raw_csv_data_path):
            continue
        elif not os.listdir(raw_csv_data_path):
            # print(f"The directory {raw_csv_data_path} is empty.")
            continue

        # Initialise empty DataFrames for the abundance, length and counts matrices
        abundance_mat = pd.DataFrame()  # TPM
        length_mat = pd.DataFrame()  # EffectiveLength
        counts_mat = pd.DataFrame()  # NumReads

        # Iterate through each quant csv file
        for quant_file in os.listdir(raw_csv_data_path):
            file_path = os.path.join(raw_csv_data_path, quant_file)
            # Read the csv file into a DataFrame
            # Abundance TPM matrix
            abundance_df = pd.read_csv(file_path, usecols=['Name', 'TPM'])
            # Effective Length matrix
            length_df = pd.read_csv(file_path, usecols=['Name', 'EffectiveLength'])
            # Counts NumReads matrix
            counts_df = pd.read_csv(file_path, usecols=['Name', 'NumReads'])

            # Rename 'TPM' column to the run ID (file name e.g. 'quant_DRR513083.csv')
            abundance_df = abundance_df.rename(columns={'TPM': quant_file.split('_')[1][:-4]})
            length_df = length_df.rename(columns={'EffectiveLength': quant_file.split('_')[1][:-4]})
            counts_df = counts_df.rename(columns={'NumReads': quant_file.split('_')[1][:-4]})
            # Set 'Name' as index
            abundance_df = abundance_df.set_index('Name')
            length_df = length_df.set_index('Name')
            counts_df = counts_df.set_index('Name')
            # Remove duplicates
            abundance_df = abundance_df[~abundance_df.index.duplicated(keep='first')]
            length_df = length_df[~length_df.index.duplicated(keep='first')]
            counts_df = counts_df[~counts_df.index.duplicated(keep='first')]

            # Concatenate with the main expression matrix
            # If the index (Name) does not exist in expression_matrix, NaN values will be added for other columns
            abundance_mat = pd.concat([abundance_mat, abundance_df], axis=1, sort=False)
            length_mat = pd.concat([length_mat, length_df], axis=1, sort=False)
            counts_mat = pd.concat([counts_mat, counts_df], axis=1, sort=False)

        # Calculate the length scaled TPM values
        length_scaled_tpm_mat = get_length_scaled_tpm_matrix(counts_mat, abundance_mat, length_mat)

        # Save the processed expression matrix to a CSV file
        expression_matrix_path = os.path.join(processed_data_path, f"{species}.csv")
        length_scaled_tpm_mat.to_csv(expression_matrix_path)

        print(f"\nExpression matrix for {species} created successfully.")


if __name__ == "__main__":
    raw_data_path = 'quant_files/raw'
    processed_data_path = 'quant_files/processed'
    create_expression_matrix(raw_data_path, processed_data_path)
