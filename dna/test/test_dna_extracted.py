""" DNA sequence extraction test-suite."""

import pytest # Import pytest for automated testing
import sys
import os
import csv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ensembl_api
# import ensembl_api # Import the Ensembl API module


def test_read_gene_ids_from_file():
    filepath = "gene_lists/homo_sapiens_genes.txt"
    # join current directory
    filepath = os.path.join(os.path.dirname(__file__), filepath)
    gene_ids_true = ["ENSG00000000003", "ENSG00000000005"]
    gene_ids = ensembl_api.read_gene_ids_from_file(filepath)
    assert gene_ids == gene_ids_true

def test_get_species_name():
    filepath = "gene_lists/homo_sapiens_genes.txt"
    species_name = ensembl_api.get_species_name(filepath)
    species_name_true = "homo_sapiens"
    assert species_name == species_name_true

def test_extract_homo_sapiens_dna_components():
    # Extract ground truth DNA sequence components from csv file
    filepath_true = "ground_truth_components/true_homo_sapiens_dna.csv"
    filepath_true = os.path.join(os.path.dirname(__file__), filepath_true)
    with open(filepath_true) as file:
        reader = csv.DictReader(file)
        dna_extracted_true = [gene for gene in reader]
    
    # Extract DNA sequence components from csv file using ensembl_api
    gene_ids_filepaths = ["gene_lists/homo_sapiens_genes.txt"]
    gene_ids_filepaths = [os.path.join(os.path.dirname(__file__), filepath) for filepath in gene_ids_filepaths]
    output_filepath = "csv_files"
    ensembl_api.get_data_as_csv(gene_ids_filepaths, output_filepath)
    filepath_test = output_filepath + "/" + "ensembl_data_homo_sapiens.csv"
    with open(filepath_test) as file:
        reader = csv.DictReader(file)
        dna_extracted_test = [gene for gene in reader]

    # Check that extracted components and ground truth components match
    for (dna_true, dna_test) in zip(dna_extracted_true, dna_extracted_test):
        assert dna_true["promoter"]==dna_test["promoter"]
        assert dna_true["utr5"]==dna_test["utr5"]
        assert dna_true["cds"]==dna_test["cds"]
        assert dna_true["utr3"]==dna_test["utr3"]
        assert dna_true["terminator"]==dna_test["terminator"]

ensembl_api.get_data_as_csv(["gene_lists/saccharomyces_cerevisiae_genes.txt"], "csv_files")
ensembl_api.get_data_as_csv(["gene_lists/galdieria_sulphuraria_genes.txt"], "csv_files")
ensembl_api.get_data_as_csv(["gene_lists/chlamydomonas_reinhardtii_genes.txt"], "csv_files")
ensembl_api.get_data_as_csv(["gene_lists/cyanidioschyzon_merolae_genes.txt"], "csv_files")