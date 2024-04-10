
from data_conversion_helper_functions.convert_quantsf_to_csv import convert_all_species_files
from data_conversion_helper_functions.create_expression_matrix import create_expression_matrix
from data_conversion_helper_functions.process_expression_matrix import process_expression_matrix


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


def extract_rna_data():
    """ Extract RNA expression levels from RNA-seq data.

    Use NCBI SRA API to download fastq files and process the RNA-seq data using nf-core/rna-seq workflow
    to obtain the gene expression matrix. Calculate median expression levels and RSD.
    """

    # Extracting gene expression levels.

    # Use NCBI SRA API to download fastq files containing RNA-seq data.

    # RNA-seq processing workflow (nf-core/rnaseq)
    # Extract gene expression matrix (TPM): samples vs gene_id

    # TODO Calculate RSD and median expression
    # 1x Gene ID
    # 1x Median expressions of genes with RDS < 2

    pass