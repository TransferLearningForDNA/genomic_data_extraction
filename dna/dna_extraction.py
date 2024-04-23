# Import the Ensembl API module
import os
from dna import ensembl_api, dna_feature_extraction


def query_dna_sequences_from_ensembl(output_folder: str) -> None:
    """Query and download DNA sequences for specified gene lists from the Ensembl database.

    Use pre-defined file paths to locate gene lists and download their respective
    DNA sequences using Ensembl REST API, saving them as CSV files in a specified directory.

    Args:
        output_folder (str): Path to the output folder where the extracted DNA
                            sequences will be stored.

    Returns:
        None: This function does not return a value but outputs files to the specified directory.
    """
    # Specify the folder containing gene lists
    folder = "dna/gene_lists/"

    # Get the list of file paths for gene lists
    all_files = os.listdir(folder)
    file_paths = [f for f in all_files if os.path.isfile(os.path.join(folder, f))]

    # file_paths = ["homo_sapiens_genes_small.txt"]  # Test with a small dataset (example)

    # Prepend the folder path to each file path
    file_paths = [folder + path for path in file_paths]

    print(file_paths)

    # Call the function to get data from Ensembl API and save it as CSV files
    ensembl_api.get_data_as_csv(file_paths, output_folder)


def extract_dna_data() -> None: # pragma: no cover, extracting dna data
    """Extract and process DNA genomic data.

    Query DNA sequences from the Ensembl database, compute necessary gene components
    and calculate codon frequency, GC content, and sequence length.

    Returns:
        None: This function does not return a value but outputs or modifies files in the specified directories.
    """
    # Extracting genomic data.
    extracted_dna_storage_folder = "dna/csv_files"

    # Query sequences to gene components from Ensembl
    query_dna_sequences_from_ensembl(extracted_dna_storage_folder)

    # Calculate genomic features
    dna_feature_extraction.extract_dna_features(extracted_dna_storage_folder)
    print("\nExtraction of DNA features is now complete!\n")
