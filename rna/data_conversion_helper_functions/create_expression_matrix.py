import os
import pandas as pd


def get_length_scaled_tpm_matrix(
    counts_mat: pd.DataFrame, abundance_mat: pd.DataFrame, length_mat: pd.DataFrame
) -> pd.DataFrame:
    """Generate length scaled TPM matrix.

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


import os
import pandas as pd


def create_expression_matrix(raw_data_path: str, processed_data_path: str) -> None:
    """Create the expression matrices for all species.

    Args:
        raw_data_path (str): Path to the folder containing raw quant files.
        processed_data_path (str): Path to store the processed expression matrix csv files.

    Returns:
        None: This function does not return a value but outputs files to the specified directory.
    """
    if not os.path.isdir(raw_data_path):
        print(f"The provided path {raw_data_path} is not a directory.")
        return
    for species in os.listdir(raw_data_path):
        raw_csv_data_path = os.path.join(raw_data_path, species, "csv_files")
        if not os.path.isdir(raw_csv_data_path):
            continue
        if not os.listdir(raw_csv_data_path):
            continue
        abundance_mat = pd.DataFrame()
        length_mat = pd.DataFrame()
        counts_mat = pd.DataFrame()
        for quant_file in os.listdir(raw_csv_data_path):
            file_path = os.path.join(raw_csv_data_path, quant_file)
            abundance_df = pd.read_csv(file_path, usecols=["Name", "TPM"]).set_index(
                "Name"
            )
            length_df = pd.read_csv(
                file_path, usecols=["Name", "EffectiveLength"]
            ).set_index("Name")
            counts_df = pd.read_csv(file_path, usecols=["Name", "NumReads"]).set_index(
                "Name"
            )
            run_id = quant_file.split("_")[1][:-4]
            abundance_df.rename(columns={"TPM": run_id}, inplace=True)
            length_df.rename(columns={"EffectiveLength": run_id}, inplace=True)
            counts_df.rename(columns={"NumReads": run_id}, inplace=True)
            abundance_df = abundance_df[~abundance_df.index.duplicated(keep="first")]
            length_df = length_df[~length_df.index.duplicated(keep="first")]
            counts_df = counts_df[~counts_df.index.duplicated(keep="first")]
            abundance_mat = pd.concat([abundance_mat, abundance_df], axis=1, sort=False)
            length_mat = pd.concat([length_mat, length_df], axis=1, sort=False)
            counts_mat = pd.concat([counts_mat, counts_df], axis=1, sort=False)

        length_scaled_tpm_mat = get_length_scaled_tpm_matrix(
            counts_mat, abundance_mat, length_mat
        )
        expression_matrix_path = os.path.join(processed_data_path, f"{species}.csv")
        length_scaled_tpm_mat.to_csv(expression_matrix_path)
        print(f"\nExpression matrix for {species} created successfully.")


if __name__ == "__main__":  # pragma: no cover, create expression matrix
    path_to_raw_data = "quant_files/raw"
    path_to_processed_data = "quant_files/processed"
    create_expression_matrix(path_to_raw_data, path_to_processed_data)
