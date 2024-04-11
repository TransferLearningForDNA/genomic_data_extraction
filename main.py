""" Expression Prediction Data Preprocessing Pipeline."""
import argparse
from dna.dna_extraction import extract_dna_data
from rna.rna_extraction import download_rna_data, process_rna_expression_data
from dataset_integration import import_species_data, merge_datasets


def run_pipeline() -> None:
    """ Run the entire expression prediction data preprocessing pipeline."""
    parser = argparse.ArgumentParser(description='Expression Prediction Data Preprocessing Pipeline.')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Adding sub-commands
    parser_extract_dna = subparsers.add_parser('extract_dna_data',
                                               help='Query genomic sequences from Ensembl and extract DNA features.')
    parser_download_rna = subparsers.add_parser('download_rna_data',
                                                help='Download fastq files containing mRNA expression data from NCBI SRA.')
    parser_download_rna.add_argument('output_directory', type=str,
                                     help='Please provide the full output file path (Warning: Large files!)')
    # parser_process_expression = subparsers.add_parser('process_expression_data', help='Process expression data')

    args = parser.parse_args()

    # Load species data from csv (dict species names:tax IDs)
    species = import_species_data('species_ids.csv')

    if args.command == 'extract_dna_data':
        extract_dna_data()
    elif args.command == 'download_rna_data':
        if not args.output_directory:
            print("Please provide the full output file path (Warning: large files!)")
            return
        download_rna_data(species_data=species, output_directory=args.output_directory)
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
