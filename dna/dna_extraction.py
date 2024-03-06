# Import the Ensembl API module
from dna import ensembl_api, dna_feature_extraction


def query_dna_sequences_from_ensembl(output_folder):
    """ Query and download DNA sequences for specified gene lists from the Ensembl database.

    Use pre-defined file paths to locate gene lists and download their respective
    DNA sequences using Ensembl REST API, saving them as CSV files in a specified directory.

    Args:
        output_folder (str): Path to the output folder where the extracted DNA
                            sequences will be stored
    """
    # TODO find how to download gene lists directly via the API
    # Specify the folder containing gene lists
    folder = "dna/gene_lists/"
    # Specify the list of file paths for gene lists
    # Original: file_paths = ["homo_sapiens_genes.txt", "saccharomyces_cerevisiae_genes.txt"]
    file_paths = ["homo_sapiens_genes_small.txt"]

    # Prepend the folder path to each file path
    file_paths = [folder + path for path in file_paths]

    # TODO save CSV files directly to One Drive?
    # Call the function to get data from Ensembl API and save it as CSV files
    ensembl_api.get_data_as_csv(file_paths, output_folder)


def extract_dna_data():
    """ Extract and process DNA genomic data.

    Query DNA sequences from the Ensembl database, compute necessary gene components
    and calculate codon frequency, GC content, and sequence length. Prepare the genomic
    data for further analysis.
    """
    # DNA: Extracting genomic data.
    extracted_dna_storage_folder = "dna/csv_files"
    # Query or compute sequences to gene components
    # (for now using only Ensembl)
    query_dna_sequences_from_ensembl(extracted_dna_storage_folder)

    # TODO use NCBI datasets to download fasta and gff files to compute DNA sequences

    # TODO Calculate codon frequency, GC content, length

    # TODO Put together all columns for genomic data
    # 1x Gene ID
    # 5x Sequences of components
    # 64x Codon frequencies of cds
    # 3x Lengths of cds, utr5, utr3
    # 3x GC content of cds, utr5, utr3
    # 2x GC content of wobble
    dna_feature_extraction.extract_dna_features(extracted_dna_storage_folder)