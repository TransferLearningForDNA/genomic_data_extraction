""" Expression Prediction Data Preprocessing Pipeline."""

import argparse
from dna.dna_extraction import extract_dna_data
from rna.rna_extraction import download_rna_data, process_rna_expression_data
from dataset_integration import import_species_data, merge_datasets


def run_pipeline() -> None:
    """ Run steps of the expression prediction data preprocessing pipeline via CLI commands."""

    parser = argparse.ArgumentParser(
        description="Expression Prediction Data Preprocessing Pipeline."
    )
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Adding sub-commands
    parser_extract_dna = subparsers.add_parser(
        "extract_dna_data",
        help="Query genomic sequences from Ensembl and extract DNA features.",
    )
    parser_download_rna = subparsers.add_parser(
        "download_rna_data",
        help="Download fastq files containing mRNA expression data from NCBI SRA.",
    )
    parser_download_rna.add_argument(
        "output_directory",
        type=str,
        help="Please provide the full output file path (Warning: Large files!)",
    )
    parser_download_rna.add_argument(
        "file_number_limit",
        type=int,
        help="Max number of files to download. Defaults to 10."
    )
    parser_process_rna_expression = subparsers.add_parser(
        "process_rna_expression",
        help="Process raw transcriptomic data to filter genes and "
        "obtain median expression of each gene.",
    )
    parser_merge_datasets = subparsers.add_parser(
        "merge_datasets",
        help="Merge processed genomic and transcriptomic data to obtain final dataset.",
    )

    args = parser.parse_args()

    # Load species data from csv (dict species names:tax IDs)
    species = import_species_data("species_ids.csv")

    if args.command == "extract_dna_data":
        # Query genomic sequences from Ensembl and extract DNA features.
        extract_dna_data()
    elif args.command == "download_rna_data":
        # Download fastq files containing mRNA expression data from NCBI SRA.
        if not args.output_directory:
            print("Please provide the full output file path (Warning: large files!)")
            return
        if not args.file_number_limit:
            print("The file number limit was not specified. Maximum 10 files will be downloaded (default).")
            download_rna_data(species_data=species, output_directory=args.output_directory)
        else:
            download_rna_data(species_data=species, output_directory=args.output_directory, file_number_limit=args.file_number_limit)
    elif args.command == "process_rna_expression":
        # Process raw quant.sf files from the nf-core/rnaseq pipeline to obtain median expression for each gene
        process_rna_expression_data()
    elif args.command == "merge_datasets":
        # Merge processed genomic and transcriptomic data to obtain final dataset.
        species_names = list(species.keys())
        for species_name in species_names:
            species_name = "_".join(species_name.lower().split(" "))
            merge_datasets(species_name=species_name)


if __name__ == "__main__":
    run_pipeline()
