import subprocess
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from rna.rna_download_logic.query_and_csv_production import (
    query_sra,
    query_and_get_srx_accession_ids,
    SRX_to_SRR_csv,
)
from rna.rna_download_logic.mRNA_fastq_download import download_sra_data


@pytest.fixture
def mock_sra_search():
    with patch("rna.rna_download_logic.query_and_csv_production.SraSearch") as mock:
        yield mock


@pytest.fixture
def mock_query_sra():
    with patch("rna.rna_download_logic.query_and_csv_production.query_sra") as mock:
        yield mock


@pytest.fixture
def mock_csv_data():
    return pd.DataFrame(
        {
            "species": ["Homo sapiens"],
            "taxonomy_id": [9606],
            "srx_id": ["DRX469035"],
            "srr_id": ["DRR484809"],
        }
    )


def test_query_sra_successful(mock_sra_search):
    instance = mock_sra_search.return_value
    instance.get_df.side_effect = [
        pd.DataFrame(
            {
                "sample_taxon_id": ["9606", "9606"],
                "experiment_accession": ["SRX123", "SRX124"],
            }
        ),
        pd.DataFrame(),
    ]

    expected_df = pd.DataFrame(
        {
            "sample_taxon_id": ["9606", "9606"],
            "experiment_accession": ["SRX123", "SRX124"],
        }
    )

    result = query_sra("Homo sapiens", 9606)
    pd.testing.assert_frame_equal(result, expected_df)


def test_query_sra_no_data_found(mock_sra_search):
    mock_sra_search.return_value.get_df.return_value = pd.DataFrame()

    result = query_sra("Unknown Species", 9999)
    assert result is None


def test_query_sra_exception_handling(mock_sra_search):
    mock_sra_search.return_value.search.side_effect = Exception("API failure")

    result = query_sra("Homo sapiens", 9606)
    assert result is None


def test_query_and_get_srx_accession_ids_no_data(mock_sra_search):
    mock_query_sra.return_value = None
    result = query_and_get_srx_accession_ids({"Homo sapiens": 9606})
    assert result == {}


def test_query_and_get_srx_accession_ids_valid_data(mock_query_sra):
    mock_query_sra.return_value = pd.DataFrame(
        {"experiment_accession": ["SRX123456", "SRX654321"]}
    )
    expected_result = {"Homo sapiens": ["SRX123456", "SRX654321"]}
    result = query_and_get_srx_accession_ids({"Homo sapiens": 9606})
    converted_result = {
        k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in result.items()
    }
    assert converted_result == expected_result, "Expected dictionary with valid SRX IDs"


def test_query_and_get_srx_accession_ids_multiple_species(mock_query_sra):
    mock_query_sra.side_effect = [
        pd.DataFrame({"experiment_accession": ["SRX123456"]}),
        pd.DataFrame({"experiment_accession": ["SRX987654"]}),
    ]
    species_data = {"Homo sapiens": 9606, "Mus musculus": 10090}
    expected_result = {"Homo sapiens": ["SRX123456"], "Mus musculus": ["SRX987654"]}
    result = query_and_get_srx_accession_ids(species_data)
    assert result == expected_result


def test_SRX_to_SRR_csv_writes_correct_data_to_file():
    with patch(
        "rna.rna_download_logic.query_and_csv_production.pd.DataFrame.to_csv"
    ) as mock_to_csv:
        species_srx_map = {"Homo sapiens": ["SRX123456"]}
        SRX_to_SRR_csv(species_srx_map, "dummy_path.csv")
        mock_to_csv.assert_called_once()


def test_download_sra_data_limit_reached():
    with patch(
        "rna.rna_download_logic.mRNA_fastq_download.os.path.exists"
    ) as mock_exists, patch(
        "rna.rna_download_logic.mRNA_fastq_download.subprocess.run"
    ) as mock_run:
        mock_exists.return_value = True
        download_sra_data("dummy.csv", "dummy_dir", 0)
        mock_run.assert_not_called()


def test_download_sra_data_limit_reached():
    mock_csv_data = pd.DataFrame(
        {
            "species": ["Homo sapiens", "Homo sapiens"],
            "taxonomy_id": [9606, 9606],
            "srx_id": ["DRX469035", "DRX469034"],
            "srr_id": ["DRR484809", "DRR484808"],
        }
    )

    with patch("pandas.read_csv", return_value=mock_csv_data) as mock_read_csv, patch(
        "os.path.exists", return_value=False
    ) as mock_exists, patch("os.makedirs") as mock_makedirs, patch(
        "subprocess.run"
    ) as mock_run:

        download_sra_data("dummy.csv", "dummy_dir", 0)

        mock_read_csv.assert_called_once_with("dummy.csv")
        mock_makedirs.assert_called_once_with("dummy_dir")
        mock_exists.assert_called()
        mock_run.assert_not_called()


def test_download_sra_data_reads_csv_correctly(mock_csv_data):
    with patch("pandas.read_csv", return_value=mock_csv_data) as mock_read_csv:
        with patch("os.path.exists", return_value=False), patch("os.makedirs"), patch(
            "subprocess.run"
        ):
            download_sra_data("dummy.csv", "dummy_dir")
        mock_read_csv.assert_called_once_with("dummy.csv")