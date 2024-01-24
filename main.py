""" Genomic data extraction pipeline."""

# Import the Ensembl API module
from dna import ensembl_api

# DNA: Extracting genomic data.

# TODO Helena's par

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


# RNA: Extracting mRNA expression levels.
