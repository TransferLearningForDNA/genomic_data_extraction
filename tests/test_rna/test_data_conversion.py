import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from rna.rna_download_logic.query_and_csv_production import query_and_get_srx_accession_ids, SRX_to_SRR_csv
from rna.rna_download_logic.mRNA_fastq_download import download_sra_data

@pytest.fixture
def mock_sra_search():
    with patch('rna.rna_download_logic.query_and_csv_production.SraSearch') as mock:
        mock.return_value.get_df.return_value = pd.DataFrame()
        yield mock

def test_query_and_get_srx_accession_ids_no_data(mock_sra_search):
    assert query_and_get_srx_accession_ids({"Homo sapiens": 9606}) == {}

def test_SRX_to_SRR_csv_writes_correct_data_to_file():
    with patch('rna.rna_download_logic.query_and_csv_production.pd.DataFrame.to_csv') as mock_to_csv:
        species_srx_map = {'Homo sapiens': ['SRX123456']}
        SRX_to_SRR_csv(species_srx_map, "dummy_path.csv")
        mock_to_csv.assert_called_once()

def test_download_sra_data_limit_reached():
    with patch('rna.rna_download_logic.mRNA_fastq_download.os.path.exists') as mock_exists, \
         patch('rna.rna_download_logic.mRNA_fastq_download.subprocess.run') as mock_run:
        mock_exists.return_value = True
        download_sra_data("dummy.csv", "dummy_dir", 0)
        mock_run.assert_not_called()