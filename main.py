""" Genomic and mRNA data extraction pipeline."""

# Import the Ensembl API module
from dna import ensembl_api


def query_dna_sequences_from_ensembl():
    # Specify the folder containing gene lists
    folder = "dna/gene_lists/"
    # Specify the list of file paths for gene lists
    # Original: file_paths = ["homo_sapiens_genes.txt", "saccharomyces_cerevisiae_genes.txt"]
    file_paths = ["homo_sapiens_genes_small.txt"]

    # Prepend the folder path to each file path
    file_paths = [folder + path for path in file_paths]

    # TODO save CSV files directly to One Drive?
    # Call the function to get data from Ensembl API and save it as CSV files
    ensembl_api.get_data_as_csv(file_paths, "dna/csv_files")


def extract_dna_data():
    # DNA: Extracting genomic data.

    # Query or compute sequences to gene components
    # (for now using only Ensembl)
    query_dna_sequences_from_ensembl()

    # TODO use NCBI datasets to download fasta and gff files to compute DNA sequences

    # TODO Calculate codon frequency, GC content, length

    # TODO Put together all columns for genomic data
    # 1x Gene ID
    # 5x Sequences of components
    # 64x Codon frequencies of cds
    # 3x Lengths of cds, utr5, utr3
    # 3x GC content of cds, utr5, utr3
    # 2x GC content of wobble


def extract_rna_data():
    # Extracting gene expression levels.

    # Use NCBI SRA API to download fastq files containing RNA-seq data.

    # RNA-seq processing workflow (nf-core/rnaseq)
    # Extract gene expression matrix (TPM): samples vs gene_id

    # TODO Calculate RSD and median expression
    # 1x Gene ID
    # 1x Median expressions of genes with RDS < 2

    pass


def merge_datasets():
    # TODO Merge DNA and RNA data by gene_id

    # TODO Store final dataset in One Drive
    pass


def run_pipeline():
    extract_dna_data()
    extract_rna_data()
    merge_datasets()


if __name__ == "__main__":
    run_pipeline()
