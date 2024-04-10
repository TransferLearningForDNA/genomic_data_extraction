""" Expression Prediction Data Preprocessing Pipeline."""
import argparse
from dna.dna_extraction import extract_dna_data
from rna.rna_extraction import extract_rna_data, process_rna_expression_data
from dataset_integration import merge_datasets


def run_pipeline() -> None:
    """ Run the entire expression prediction data preprocessing pipeline."""
    parser = argparse.ArgumentParser(description="Expression Prediction Data Preprocessing Pipeline.")
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Adding sub-commands
    parser_extract_dna = subparsers.add_parser('extract_dna_data',
                                               help='Query genomic sequences from Ensembl and extract DNA features.')
    # parser_extract_rna = subparsers.add_parser('extract_rna_data', help='Extract RNA data')
    # parser_process_expression = subparsers.add_parser('process_expression_data', help='Process expression data')

    # You can add specific arguments to each sub-command if needed
    # For example, parser_extract_dna.add_argument(...)

    args = parser.parse_args()

    if args.command == 'extract_dna_data':
        extract_dna_data()
    elif args.command == 'extract_rna_data':
        extract_rna_data()
    elif args.command == 'process_expression_data':
        process_rna_expression_data()
    # else:
    #     # argparse will automatically show a help message for undefined commands
    #     # but you can also print your own error message if you want:
    #     parser.print_help()

    # extract_dna_data()
    # # extract_rna_data()
    #
    # # Process raw quant.sf files from the nf-core rna-seq pipeline
    # # to obtain processed median expression of transcripts
    # process_rna_expression_data()
    #
    # # Merge DNA and RNA datasets for each species
    # species_names = ['chlamydomonas_reinhardtii', 'cyanidioschyzon_merolae', 'galdieria_sulphuraria',
    #                  'homo_sapiens', 'saccharomyces_cerevisiae']
    # for species_name in species_names:
    #     merge_datasets(species_name=species_name)


if __name__ == "__main__":
    run_pipeline()
