import os
import pandas as pd


def create_expression_matrix(raw_data_path, processed_data_path):
    """ Create the expression matrices for all species."""

    # Iterate over species
    for species in os.listdir(raw_data_path):
        raw_csv_data_path = os.path.join(raw_data_path, species, 'csv_files')

        # Skip if it's not a directory (e.g., .DS_Store)
        if not os.path.isdir(raw_csv_data_path):
            continue
        elif not os.listdir(raw_csv_data_path):
            print(f"The directory {raw_csv_data_path} is empty.")
            continue

        # Initialise an empty DataFrame for the expression matrix
        expression_matrix = pd.DataFrame()

        # Iterate through each quant csv file
        for quant_file in os.listdir(raw_csv_data_path):
            file_path = os.path.join(raw_csv_data_path, quant_file)
            # Read the csv file into a DataFrame
            tpr_df = pd.read_csv(file_path, usecols=['Name', 'TPM'])

            # Rename 'TPM' column to the run ID (file name e.g. 'quant_DRR513083.csv')
            tpr_df = tpr_df.rename(columns={'TPM': quant_file.split('_')[1][:-4]})
            # Set 'Name' as index
            tpr_df = tpr_df.set_index('Name')

            # Concatenate with the main expression matrix
            # If the index (Name) does not exist in expression_matrix, NaN values will be added for other columns
            expression_matrix = pd.concat([expression_matrix, tpr_df], axis=1, sort=False)

        # Rename 'Name' column to 'transcript_id'
        expression_matrix.rename(columns={'Name': 'transcript_id'}, inplace=True)
        # Save the expression matrix to a CSV file
        expression_matrix_path = os.path.join(processed_data_path, f"{species}.csv")
        expression_matrix.to_csv(expression_matrix_path)

        print(f"Expression matrix for {species} created successfully.")


if __name__ == "__main__":
    raw_data_path = 'quant_files/raw'
    processed_data_path = 'quant_files/processed'
    create_expression_matrix(raw_data_path, processed_data_path)
