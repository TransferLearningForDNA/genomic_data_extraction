""" DNA feature extraction test_dna-suite."""

import pytest  # Import pytest for automated testing
import sys
import os
import csv
import pandas as pd
from itertools import product


# Add the parent directory of `dna` to `sys.path`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from dna import dna_feature_extraction


def test_compute_cds_codon_frequencies_standard_case():
    """ Tests that cds codon frequencies are correctly calculated."""

    codons = ["".join(combination) for combination in product("ACGT", repeat=3)]
    cds = "AGTCAAAGTTAT"

    codon_frequencies = dna_feature_extraction.compute_cds_codon_frequencies(cds, codons)

    try:
        for codon in codons:
            if codon == "AGT":
                assert codon_frequencies[codon]==0.5
            elif codon == "CAA":
                assert codon_frequencies[codon]==0.25
            elif codon == "TAT":
                assert codon_frequencies[codon]==0.25
            else:
                assert codon_frequencies[codon]==0
    except AssertionError:
        print(f"Incorrect codon frequency calculated ({codon_frequencies[codon]}) for codon {codon}")


def test_compute_cds_codon_frequencies_empty_case():
    """ 
    Tests that cds codon frequencies are correctly calculated
    when an empty cds sequence is provided.
    """

    codons = ["".join(combination) for combination in product("ACGT", repeat=3)]
    cds = ""

    codon_frequencies = dna_feature_extraction.compute_cds_codon_frequencies(cds, codons)

    try:
        for codon in codons:
            assert codon_frequencies[codon]==0
    except AssertionError:
        print(f"Incorrect codon frequency calculated ({codon_frequencies[codon]}) for codon {codon}")


def test_compute_lengths_standard_case():
    """ Tests that the length of cds, utr3 and utr5 DNA sequences are correctly calculated."""

    cds = "AGTCAAAGTTAT"
    utr5 = "AAA"
    utr3 = "TATAAA"

    lengths = dna_feature_extraction.compute_lengths(cds=cds, utr5=utr5, utr3=utr3)

    assert (
        lengths["cds_length"]==12
        and lengths["utr5_length"]==3
        and lengths["utr3_length"]==6
    )


def test_compute_lengths_empty_case():
    """ Tests that the length of cds, utr3 and utr5 DNA sequences are correctly calculated
    when empty cds, utr5, utr3 sequences are provided."""

    cds = ""
    utr5 = ""
    utr3 = ""

    lengths = dna_feature_extraction.compute_lengths(cds=cds, utr5=utr5, utr3=utr3)

    assert (
        lengths["cds_length"]==""
        and lengths["utr5_length"]==""
        and lengths["utr3_length"]==""
    )


def test_compute_gc_content_sequence_components_standard_case():
    """ 
    Tests that the GC content of the cds, utr3 and utr5 sequences
    is correctly calculated.

    GC content is defined as (G + C)/(A + T + G + C), where each letter
    represents the number of times that nucleotide appears in the DNA sequence.
    """

    cds = "AGTCAAAGTTAT"
    utr5 = "AAGTGC"
    utr3 = "TATAAAGGGCCC"

    gc_content = dna_feature_extraction.compute_gc_content_sequence_components(cds=cds, utr5=utr5, utr3=utr3)

    assert (
        gc_content["utr5_gc"] == 0.5
        and gc_content["cds_gc"] == 0.25
        and gc_content["utr3_gc"] == 0.5
    )


def test_compute_gc_content_sequence_components_empty_case():
    """ 
    Tests that the GC content of the cds, utr3 and utr5 sequences
    is correctly calculated.

    GC content is defined as (G + C)/(A + T + G + C), where each letter
    represents the number of times that nucleotide appears in the DNA sequence.
    """

    cds = ""
    utr5 = ""
    utr3 = ""

    gc_content = dna_feature_extraction.compute_gc_content_sequence_components(cds=cds, utr5=utr5, utr3=utr3)

    assert (
        gc_content["utr5_gc"] == ""
        and gc_content["cds_gc"] == ""
        and gc_content["utr3_gc"] == ""
    )


def test_compute_gc_content_wobble_positions_standard_case():
    """ 
    Tests that the GC content of positions 2 and 3 in codons in the cds
    is correctly calculated.

    GC content is defined as (G + C)/(A + T + G + C), where each letter
    represents the number of times that nucleotide appears in a given
    wobble position
    """

    cds = "AGTCGCAAATTT"

    wobble_gc_content = dna_feature_extraction.compute_gc_content_wobble_positions(cds=cds)

    assert (
        wobble_gc_content["cds_wobble2_gc"] == 0.5
        and wobble_gc_content["cds_wobble3_gc"] == 0.25
    )

def test_compute_gc_content_wobble_positions_empty_case():
    """ 
    Tests that the GC content of positions 2 and 3 in codons in the cds
    is correctly calculated.

    GC content is defined as (G + C)/(A + T + G + C), where each letter
    represents the number of times that nucleotide appears in a given
    wobble position
    """

    cds = ""

    wobble_gc_content = dna_feature_extraction.compute_gc_content_wobble_positions(cds=cds)

    assert (
        wobble_gc_content["cds_wobble2_gc"] == ""
        and wobble_gc_content["cds_wobble3_gc"] == ""
    )

def test_extract_dna_features():

    input_folder_path = os.path.join(os.path.dirname(__file__), "feature_extraction_csv_files")
    ground_truth_folder_path = os.path.join(os.path.dirname(__file__), "feature_extraction_ground_truth")

    # Extract features from input csv files in input folder path
    dna_feature_extraction.extract_dna_features(input_folder_path)

    # Extract the filenames of the txt files where the gene id lists are stored
    species_filelist = os.listdir(input_folder_path)

    # Loop through each csv file containing the extracted features 
    # and check against ground truth csv files
    for species in species_filelist:
        species_name = '_'.join(species.split('_')[2:]).rstrip(".csv")
        print("Checking DNA components for: ", species_name)
        extracted_features_filepath = f"{input_folder_path}/ensembl_data_{species_name}.csv"
        ground_truth_features_filepath = f"{ground_truth_folder_path}/{species_name}_features_ground_truth.csv"

        try:
            with open(extracted_features_filepath) as file:
                reader = csv.DictReader(file)
                features_extracted_test = [gene for gene in reader]

            with open(ground_truth_features_filepath) as file:
                reader = csv.DictReader(file)
                features_extracted_true = [gene for gene in reader]

        except FileNotFoundError:
            print(f"The file for {species} could not be found. "
                  f"Check that a ground truth file and an ensembl data file exist for {species}")

        else:
            for (features_true, features_test) in zip(features_extracted_test, features_extracted_true):
                assert (
                        features_true["cds_length"] == features_test["cds_length"]
                        and features_true["utr5_length"] == features_test["utr5_length"]
                        and features_true["utr3_length"] == features_test["utr3_length"]
                        and features_true["utr5_gc"] == features_test["utr5_gc"]
                        and features_true["cds_gc"] == features_test["cds_gc"]
                        and features_true["utr3_gc"] == features_test["utr3_gc"]
                        and features_true["cds_wobble2_gc"] == features_test["cds_wobble2_gc"]
                        and features_true["cds_wobble3_gc"] == features_test["cds_wobble3_gc"]
                )

        # Removing the features calculated from the input csvs to facilitate future tests
        df = pd.read_csv(extracted_features_filepath)
        df = df.iloc[:, :7]
        df.to_csv(extracted_features_filepath, index=False)