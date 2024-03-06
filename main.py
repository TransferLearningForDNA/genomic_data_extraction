""" Expression Prediction Data Preprocessing Pipeline."""

from dna_extraction import extract_dna_data
from rna_extraction import extract_rna_data
from dataset_integration import merge_datasets


def run_pipeline():
    """ Run the entire expression prediction data preprocessing pipeline."""
    extract_dna_data()
    # extract_rna_data()

    # merge_datasets()


if __name__ == "__main__":
    run_pipeline()
