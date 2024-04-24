""" DNA sequence extraction test_dna-suite."""

import pytest  # Import pytest for automated testing
import sys
import os
import csv

# Add the parent directory of `dna` to `sys.path`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dna import ensembl_api


def test_read_gene_ids_from_file():
    filepath = os.path.join(
        os.path.dirname(__file__), "test_data/gene_lists/homo_sapiens_genes.txt"
    )
    gene_ids_true = ["ENSG00000000003", "ENSG00000000005"]
    gene_ids = ensembl_api.read_gene_ids_from_file(filepath)
    assert gene_ids == gene_ids_true


def test_get_species_name():
    filepath = os.path.join(
        os.path.dirname(__file__), "test_data/gene_lists/homo_sapiens_genes.txt"
    )
    species_name = ensembl_api.get_species_name(filepath)
    species_name_true = "homo_sapiens"
    assert species_name == species_name_true


def test_check_extracted_components():
    # Define the folder where gene ids of the 5 mandatory species are stored
    gene_ids_folderpath = os.path.join(os.path.dirname(__file__), "test_data/gene_lists")
    # Define the folder where the extracted dna sequences should be stored
    output_filepath = os.path.join(os.path.dirname(__file__), "test_data/csv_files")

    # Extract the filenames of the txt files where the gene id lists are stored
    gene_ids_filelist = os.listdir(gene_ids_folderpath)
    # Extract DNA sequence components into csv files using ensembl_api
    for species in gene_ids_filelist:
        gene_ids_filepath = os.path.join(gene_ids_folderpath, species)
        ensembl_api.get_data_as_csv([gene_ids_filepath], output_filepath)

    # Loop through each csv file containing the extracted sequence components
    # and check against ground truth csv files
    for species in gene_ids_filelist:
        species_name = "_".join(species.split("_")[:2])
        print("Checking DNA components for: ", species_name)
        extracted_dna_filepath = os.path.join(
            output_filepath, f"ensembl_data_{species_name}.csv"
        )
        ground_truth_dna_filepath = os.path.join(
            os.path.dirname(__file__),
            f"test_data/ground_truth_components/true_{species_name}_dna.csv",
        )

        try:
            with open(extracted_dna_filepath) as file:
                reader = csv.DictReader(file)
                dna_extracted_test = [gene for gene in reader]

            with open(ground_truth_dna_filepath) as file:
                reader = csv.DictReader(file)
                dna_extracted_true = [gene for gene in reader]

        except FileNotFoundError:
            print(
                f"The file for {species} could not be found. "
                f"Check that a ground truth file and an ensembl data file exist for {species}"
            )
        else:
            for dna_true, dna_test in zip(dna_extracted_true, dna_extracted_test):
                assert (
                    dna_true["promoter"] == dna_test["promoter"]
                    and dna_true["utr5"] == dna_test["utr5"]
                    and dna_true["cds"] == dna_test["cds"]
                    and dna_true["utr3"] == dna_test["utr3"]
                    and dna_true["terminator"] == dna_test["terminator"]
                )