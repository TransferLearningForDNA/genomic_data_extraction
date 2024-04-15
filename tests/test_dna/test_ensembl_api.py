import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
# Add the parent directory of `dna` to `sys.path`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from dna import ensembl_api
import ensembl_rest


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


