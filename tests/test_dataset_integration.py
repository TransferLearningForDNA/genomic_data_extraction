import sys
import os

import pandas as pd
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from dataset_integration import merge_datasets, import_species_data


def test_import_species_data():
    mock_csv_data = pd.DataFrame(
        {"name": ["Homo sapiens", "Mus musculus"], "tax_id": [9606, 10090]}
    )

    with patch("pandas.read_csv", return_value=mock_csv_data) as mock_read_csv:
        result = import_species_data("dummy_path.csv")
        mock_read_csv.assert_called_once_with("dummy_path.csv")
        assert result == {"Homo sapiens": 9606, "Mus musculus": 10090}


def test_merge_datasets():
    mock_dna_data = pd.DataFrame(
        {"transcript_id": ["tx1", "tx2"], "gene_info": ["geneA", "geneB"]}
    )
    mock_rna_data = pd.DataFrame(
        {"transcript_id": ["tx1", "tx2"], "expression": [5.5, 7.2]}
    )

    expected_merged_data = pd.DataFrame(
        {
            "transcript_id": ["tx1", "tx2"],
            "gene_info": ["geneA", "geneB"],
            "expression": [5.5, 7.2],
        }
    )

    with patch("os.path.exists", return_value=True), patch(
        "pandas.read_csv", side_effect=[mock_dna_data, mock_rna_data]
    ) as mock_read_csv, patch("pandas.DataFrame.to_csv") as mock_to_csv:

        result = merge_datasets("homo_sapiens")

        assert mock_read_csv.call_count == 2
        pd.testing.assert_frame_equal(result, expected_merged_data)
        mock_to_csv.assert_called_once_with(
            "merged_csv_files/merged_homo_sapiens_data.csv", index=False
        )
