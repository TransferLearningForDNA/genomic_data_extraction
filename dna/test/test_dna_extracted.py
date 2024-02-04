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

def test_check_extracted_components():
    # Extract DNA sequence components from csv file using ensembl_api
    gene_ids_folderpath = "gene_lists"
    gene_ids_folderpath = os.path.join(os.path.dirname(__file__), gene_ids_folderpath)
    gene_ids_filelist = os.listdir(gene_ids_folderpath)
    output_filepath = "csv_files"
    for species in gene_ids_filelist:
        gene_ids_filepath = gene_ids_folderpath + "/" + species
        ensembl_api.get_data_as_csv([gene_ids_filepath], output_filepath)
    
    # Loop through each file of extracted DNA and check against ground truth files
    species_names = ['_'.join(species.split('_')[:2]) for species in gene_ids_filelist]
    for species in species_names:
        print("Checking DNA components for: ", species)
        extracted_dna_filepath = output_filepath + "/ensembl_data_" + species + ".csv"
        extracted_dna_filepath = os.path.join(os.path.dirname(__file__), extracted_dna_filepath)
        ground_truth_dna_filepath = "ground_truth_components/true_" + species + "_dna.csv"
        ground_truth_dna_filepath = os.path.join(os.path.dirname(__file__), ground_truth_dna_filepath)
        
        try:
            with open(extracted_dna_filepath) as file:
                reader = csv.DictReader(file)
                dna_extracted_test = [gene for gene in reader]
            
            with open(ground_truth_dna_filepath) as file:
                reader = csv.DictReader(file)
                dna_extracted_true = [gene for gene in reader]
        except FileNotFoundError:
            print(f"The file for {species} could not be found. Check that a ground truth file and an ensembl data file exist for {species}")
        else:
            # Check that extracted components and ground truth components match
            for (dna_true, dna_test) in zip(dna_extracted_true, dna_extracted_test):
                assert dna_true["promoter"]==dna_test["promoter"]
                assert dna_true["utr5"]==dna_test["utr5"]
                assert dna_true["cds"]==dna_test["cds"]
                assert dna_true["utr3"]==dna_test["utr3"]
                assert dna_true["terminator"]==dna_test["terminator"]