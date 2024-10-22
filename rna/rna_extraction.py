import os
from typing import Dict, Optional
from rna.data_conversion_helper_functions.convert_quantsf_to_csv import (
    convert_all_species_files,
)
from rna.data_conversion_helper_functions.create_expression_matrix import (
    create_expression_matrix,
)
from rna.data_conversion_helper_functions.process_expression_matrix import (
    process_expression_matrix,
)
from rna.rna_download_logic.query_and_csv_production import (
    query_and_get_srx_accession_ids,
    SRX_to_SRR_csv,
)
from rna.rna_download_logic.mRNA_fastq_download import download_sra_data


def process_rna_expression_data() -> None:
    """Process raw transcriptomic data to filter genes and obtain median expression of each gene."""

    print("\nProcessing RNA expression data.\n")

    # Convert raw quant.sf files (output of nf-core rna-seq pipeline) to csv files.
    raw_data_path = "rna/quant_files/raw"  # path to raw quant files folder
    convert_all_species_files(raw_data_path)

    # Create expression matrices of length scaled TPM values, indexed by transcript ID.
    processed_data_path = "rna/quant_files/processed"
    create_expression_matrix(raw_data_path, processed_data_path)

    # Process expression matrices to filter for transcript with RSD < 2 and calculate median expression
    median_expression_path = "rna/median_expression_files"
    process_expression_matrix(processed_data_path, median_expression_path)


def create_directories_for_species(
    species_data: Dict[str, int], base_directory: str
) -> None:
    """Creates directories for storing quantification files.

    Args:
        species_data (Dict[str, int]): Dictionary with species names as keys.
        base_directory (str): Base directory path under which to create species directories.
    """
    for species_name in species_data.keys():
        # Format the species name to be lowercase and linked with an underscore
        formatted_species_name = "_".join(species_name.lower().split())
        species_directory = os.path.join(base_directory, formatted_species_name)

        # Create main directory for the species
        os.makedirs(species_directory, exist_ok=True)

        # Create subdirectories for sf_files (nf-core/rnaseq output) and csv_files (converted files)
        os.makedirs(os.path.join(species_directory, "sf_files"), exist_ok=True)
        os.makedirs(os.path.join(species_directory, "csv_files"), exist_ok=True)

        print(f"Created directories for {species_name} at {species_directory}.")


def download_rna_data(
    species_data: Dict[str, int],
    output_directory: str,
    file_number_limit: Optional[int] = 10,
) -> None:
    """Download fastq files containing RNA-seq data from NCBI SRA API

    Args:
        species_data (Dict[str, int]): A dictionary with species names as keys and tax IDs as values.
        output_directory (str): Full directory path where the downloaded files will be stored.
        file_number_limit (int): Maximum number of files to download per species (defaults to 10).
    """

    # First, create necessary directories for each species for later processing
    create_directories_for_species(species_data, "quant_files/raw")

    print(f"Downloading RNA data to {output_directory}. \nSpecies: {species_data}")

    # Obtain experiment accession numbers for each species
    # Query NCBI SRA Database to obtain species metadata
    species_srx_map = query_and_get_srx_accession_ids(
        species_data, limit=file_number_limit
    )

    # Storing only the needed data - SRX and SRR IDs - in a csv
    csv_file_path = "rna/output_srx_srr.csv"
    SRX_to_SRR_csv(species_srx_map, output_file=csv_file_path)

    # Use NCBI SRA API to download fastq files containing RNA-seq data
    total_number_of_files = file_number_limit * len(species_data)
    download_sra_data(csv_file_path, output_directory, limit=total_number_of_files)

    # (Optional) View the returned metadata
    # all_species_metadata = view_srx_metadata(species_srx_map)
    # print(all_species_metadata['Homo sapiens'].head(5))


if __name__ == "__main__":
    process_rna_expression_data()
