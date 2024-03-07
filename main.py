""" Expression Prediction Data Preprocessing Pipeline."""

from dna_extraction import extract_dna_data
from rna_extraction import extract_rna_data
from dataset_integration import merge_datasets, process_rna_expression_data


def run_pipeline():
    """ Run the entire expression prediction data preprocessing pipeline."""
    extract_dna_data()
    # extract_rna_data()

    # Process raw quant.sf files from the nf-core rna-seq pipeline
    # to obtain processed median expression of transcripts
    process_rna_expression_data()

    # Merge DNA and RNA datasets for each species
    species_names = ['chlamydomonas_reinhardtii', 'cyanidioschyzon_merolae', 'galdieria_sulphuraria',
                     'homo_sapiens', 'saccharomyces_cerevisiae']
    for species_name in species_names:
        merge_datasets(species_name=species_name)


if __name__ == "__main__":
    run_pipeline()
