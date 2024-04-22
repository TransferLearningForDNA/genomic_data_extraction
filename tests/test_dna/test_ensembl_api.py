import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
# Add the parent directory of `dna` to `sys.path`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from dna import ensembl_api
import ensembl_rest
import csv


def test_get_cds_valid_id(sequence_PNW69574):
    transcript_id = "PNW69574"
    cds_sequence = ensembl_api.get_cds(transcript_id)
    assert cds_sequence == sequence_PNW69574

def test_get_cds_invalid_id():
    transcript_id = "invalid_id"
    cds_sequence = ensembl_api.get_cds(transcript_id)
    assert cds_sequence == ''


def test_get_promoter_terminator(promoter_terminator_PNW69574):
    transcript_id = "PNW69574"
    expected_promoter, expected_terminator = promoter_terminator_PNW69574
    promoter, terminator = ensembl_api.get_promoter_terminator(transcript_id)

    assert promoter == expected_promoter
    assert terminator == expected_terminator

def test_bad_request_promoter_terminator():
    transcript_id = "WRONG_ID"
    promoter, terminator = ensembl_api.get_promoter_terminator(transcript_id)

    assert promoter == ''
    assert terminator == ''


def test_extract_utr_information(utr_data):

    # Unpack the data
    data, expected_utr5, expected_utr3, expected_chromosome, expected_strand = utr_data
    
    # Call the function under test
    utr5_list, utr3_list, chromosome, strand = ensembl_api.extract_utr_information(data)

    # Assertions
    assert utr5_list == expected_utr5
    assert utr3_list == expected_utr3
    assert chromosome == expected_chromosome
    assert strand == expected_strand


def test_extract_utr_information_empty_data():
    # Test with empty data
    empty_data = {}
    utr5_list, utr3_list, chromosome, strand = ensembl_api.extract_utr_information(empty_data)

    assert utr5_list == []
    assert utr3_list == []
    assert chromosome == None
    assert strand == None

@patch("ensembl_rest.sequence_region")
def test_get_utr_sequence(mock_sequence_region):
    # Mock input data
    chromosome = "chr1"
    strand = 1
    start = 100
    end = 200
    species = "human"

    # Mock Ensembl REST API response
    mock_response = {"seq": "ATGC"}

    # Expected output
    expected_sequence = "ATGC"

    # Call the function under test
    mock_sequence_region.return_value = mock_response
    utr_sequence = ensembl_api.get_utr_sequence(chromosome, strand, start, end, species)

    # Assertion
    assert utr_sequence == expected_sequence

@patch("ensembl_rest.sequence_region")
def test_get_full_utr_sequence(mock_get_utr_sequence):
    # Mock input data
    list_utr_coordinates = [(100, 200), (300, 400)]
    chromosome = "chr1"
    strand = 1
    species = "human"

    # Mock Ensembl REST API responses
    mock_response_1 = {"seq": "ATGC"}
    mock_response_2 = {"seq": "CGTA"}

    # Expected output
    expected_sequence = "ATGCCGTA"

    # Call the function under test
    mock_get_utr_sequence.side_effect = [mock_response_1, mock_response_2]
    utr_sequence = ensembl_api.get_full_utr_sequence(list_utr_coordinates, chromosome, strand, species)

    # Assertion
    assert utr_sequence == expected_sequence

@patch("ensembl_rest.lookup")
def test_request_with_retry(mock_lookup):
    # Mock input data
    transcript_id = "ENST00000619136"

    # Mock Ensembl REST API response
    mock_response = {"transcript_id": "ENST00000619136", "gene_id": "ENSG00000186092"}

    # Expected output
    expected_data = {"transcript_id": "ENST00000619136", "gene_id": "ENSG00000186092"}

    # Call the function under test
   
    mock_lookup.side_effect = [ensembl_rest.core.restclient.HTTPError(response=MagicMock(status_code=429)),  # First call raises rate limit error
                                    mock_response]  # Second call returns response
    with patch("time.sleep") as mock_sleep:
        mock_sleep.return_value = None
        transcript_data = ensembl_api.request_with_retry(transcript_id)

    # Assertion
    assert transcript_data == expected_data

    # Assert that ensembl_rest.lookup was called with the correct arguments
    mock_lookup.assert_called_with(id=transcript_id, params={'expand': True, 'utr': True})

    # Assert that time.sleep was called
    mock_sleep.assert_called_once_with(1)  # Assuming sleep is called with a delay of 1 second

def test_read_gene_ids_from_file():
    """ Tests that genes are read correctly by read_gene_ids_from_file in the 
    ensembl API.

    Two homo sapiens genes have been defined in gene_lists/homo_sapiens_genes.txt. 
    The function read_gene_ids_from_file() is called using that file and the 
    output of the function is compared with the ground truth gene ids.
    """
    filepath = os.path.join(os.path.dirname(__file__),
                            "gene_lists/homo_sapiens_genes.txt")
    gene_ids_true = ["ENSG00000000003", "ENSG00000000005"]
    gene_ids = ensembl_api.read_gene_ids_from_file(filepath)
    assert gene_ids == gene_ids_true


def test_get_species_name():
    """ Tests that species name is read correctly from filename by 
    get_species_name in the ensembl API."""

    filepath = os.path.join(os.path.dirname(__file__),
                            "gene_lists/homo_sapiens_genes.txt")
    species_name = ensembl_api.get_species_name(filepath)
    species_name_true = "homo_sapiens"
    assert species_name == species_name_true


def test_check_extracted_components():
    """ Tests that gene components are correctly extracted by the Ensembl API
    for mandatory species.
    
    A txt file has been created for each mandatory species containing two gene 
    ids. The Ensembl API is used to extract the gene components for the two 
    genes defined for each species. The correctness of the extracted sequences 
    is automatically verified against a folder containing the csv files with 
    the ground truth dna components for each of the genes processed.
    """

    # Define the folder where gene ids of the 5 mandatory species are stored
    gene_ids_folderpath = os.path.join(os.path.dirname(__file__), "gene_lists")
    # Define the folder where the extracted dna sequences should be stored
    output_filepath = os.path.join(os.path.dirname(__file__), "csv_files")

    # Extract the filenames of the txt files where the gene id lists are stored
    gene_ids_filelist = os.listdir(gene_ids_folderpath)
    # Extract DNA sequence components into csv files using ensembl_api
    for species in gene_ids_filelist:
        gene_ids_filepath = os.path.join(gene_ids_folderpath, species)
        ensembl_api.get_data_as_csv([gene_ids_filepath], output_filepath)

    # Loop through each csv file containing the extracted sequence components 
    # and check against ground truth csv files
    for species in gene_ids_filelist:
        species_name = '_'.join(species.split('_')[:2])
        print("Checking DNA components for: ", species_name)
        extracted_dna_filepath = os.path.join(output_filepath,
                                              f"ensembl_data_{species_name}.csv")
        ground_truth_dna_filepath = os.path.join(os.path.dirname(__file__),
                                                 f"ground_truth_components/true_{species_name}_dna.csv")

        try:
            with open(extracted_dna_filepath) as file:
                reader = csv.DictReader(file)
                dna_extracted_test = [gene for gene in reader]

            with open(ground_truth_dna_filepath) as file:
                reader = csv.DictReader(file)
                dna_extracted_true = [gene for gene in reader]

        except FileNotFoundError:
            print(f"The file for {species} could not be found. "
                  f"Check that a ground truth file and an ensembl data file exist for {species}")
        else:
            for (dna_true, dna_test) in zip(dna_extracted_true, dna_extracted_test):
                assert (
                        dna_true["promoter"] == dna_test["promoter"]
                        and dna_true["utr5"] == dna_test["utr5"]
                        and dna_true["cds"] == dna_test["cds"]
                        and dna_true["utr3"] == dna_test["utr3"]
                        and dna_true["terminator"] == dna_test["terminator"]
                )
