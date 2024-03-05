import pandas as pd
import os


def calculate_rsd(expression_matrix):
    """ Calculate the RSD values of the expression matrix.

    Args:
        expression_matrix (DataFrame)

    Returns:
        DataFrame: expression matrix appended with mean, std and RSD columns
    """

    # Calculate the mean and standard deviation across the row
    expression_matrix['mean'] = expression_matrix.iloc[:, 1:].mean(axis=1)
    expression_matrix['std_dev'] = expression_matrix.iloc[:, 1:-1].std(axis=1)
    # Calculate the RSD (Relative Standard Deviation)
    expression_matrix['rsd'] = expression_matrix['std_dev'] / expression_matrix['mean']
    # Change NaN RSD values with zero
    expression_matrix['rsd'] = expression_matrix['rsd'].fillna(0)
    return expression_matrix


def calculate_median_expression(filtered_expression_matrix):
    """ Calculate the median expression.

    Args:
        filtered_expression_matrix (DataFrame) : Expression matrix containing transcripts with RSD < 2

    Returns:
        DataFrame : with columns 'transcript_id' and 'median_expression
    """
    # Calculate the median expression across experiments/ runs
    # Exclude the 'transcript_id' column from the calculation
    median_expression = filtered_expression_matrix.drop('transcript_id', axis=1).median(axis=1)

    # Create a new DataFrame with transcript IDs and their median expressions
    median_expression_df = pd.DataFrame({
        'transcript_id': filtered_expression_matrix['transcript_id'],
        'median_expression': median_expression
    })

    return median_expression_df


def process_expression_matrix(file_path, output_file_path):
    """ Process expression matrices for each species.

    Filter for genes with RSD < 2 and calculate median expression.
    """
    # Iterate over species
    for species in os.listdir(file_path):
        expression_matrix_path = os.path.join(file_path, species)

        # # Initialise an empty DataFrame to store the median expression
        # median_expression = pd.DataFrame()

        # Read the csv file into a DataFrame
        expression_matrix_df = pd.read_csv(expression_matrix_path)
        # Rename the first column as 'transcript_id'
        expression_matrix_df.rename(columns={'Name': 'transcript_id'}, inplace=True)

        # Calculate the RSD
        matrix_expression_rsd = calculate_rsd(expression_matrix_df.copy())

        # Filter the genes with RSD < 2
        filtered_expression_matrix = expression_matrix_df[matrix_expression_rsd['rsd'] < 2]

        # Calculate the median expression
        median_expression_df = calculate_median_expression(filtered_expression_matrix)

        # Save the median matrix DataFrame to a CSV file
        median_expression_path = os.path.join(output_file_path, f"rna_expression_{species}")
        median_expression_df.to_csv(median_expression_path, index=False)


if __name__ == "__main__":
    folder = 'quant_files/processed'
    output_folder = 'median_expression_files'
    process_expression_matrix(folder, output_folder)
