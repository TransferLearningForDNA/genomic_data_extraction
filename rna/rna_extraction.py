from rna.data_conversion_helper_functions.convert_quantsf_to_csv import convert_all_species_files
from rna.data_conversion_helper_functions.create_expression_matrix import create_expression_matrix
from rna.data_conversion_helper_functions.process_expression_matrix import process_expression_matrix
from rna.rna_download_logic.query_and_csv_production import query_and_get_srx_accession_ids, SRX_to_SRR_csv
from rna.rna_download_logic.mRNA_fastq_download import download_sra_data


def process_rna_expression_data() -> None:
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


def download_rna_data(species_data: dict, output_directory: str) -> None:
    """ Download fastq files containing RNA-seq data from NCBI SRA API

    Args:
        species_data (dict): A dictionary with species names as keys and tax IDs as values.
        output_directory (str): Full directory path where the downloaded files will be stored.

    # Extract RNA expression levels from RNA-seq data.
    # Use NCBI SRA API to download fastq files and process the RNA-seq data using nf-core/rna-seq workflow
    # to obtain the gene expression matrix. Calculate median expression levels and RSD.
    """

    print(f"Downloading RNA data to {output_directory}. \nSpecies: {species_data}")

    # Obtain experiment accession numbers for each species
    # Query NCBI SRA Database to obtain species metadata
    species_srx_map = query_and_get_srx_accession_ids(species_data)

    # Storing only the needed data - SRX and SRR IDs - in a csv
    SRX_to_SRR_csv(species_srx_map, output_file='output_srx_srr.csv')

    # Use NCBI SRA API to download fastq files containing RNA-seq data
    csv_file_path = '/rna/output_srx_srr.csv'
    download_sra_data(csv_file_path, output_directory)

    # (Optional) View the returned metadata
    # all_species_metadata = view_srx_metadata(species_srx_map)
    # print(all_species_metadata['Homo sapiens'].head(5))



    # # RNA-seq processing workflow (nf-core/rnaseq)
    # # Extract gene expression matrix (TPM)
    #
    #
    # # TODO Calculate RSD and median expression
    # # 1x Gene ID
    # # 1x Median expressions of genes with RDS < 2
    #
    # pass


# if __name__ == "__main__":
    # process_rna_expression_data()
