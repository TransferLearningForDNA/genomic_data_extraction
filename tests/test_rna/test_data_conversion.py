import pytest
from unittest.mock import patch, MagicMock, mock_open, call
import csv
import pandas as pd
import os

from rna.data_conversion_helper_functions.convert_quantsf_to_csv import (
    convert_all_species_files,
    convert_quant_output_to_csv,
)
from rna.data_conversion_helper_functions.create_expression_matrix import (
    create_expression_matrix,
    get_length_scaled_tpm_matrix,
)
from rna.data_conversion_helper_functions.process_expression_matrix import (
    process_expression_matrix,
    calculate_median_expression,
    calculate_rsd,
)
from rna.data_conversion_helper_functions.create_samplesheet_csv import (
    list_files,
    create_samplesheet_for_one_species,
)
from rna.rna_extraction import create_directories_for_species

@patch("builtins.print")
@patch("os.path.isdir")
@patch("os.listdir")
def test_convert_all_species_files_no_directory(mock_listdir, mock_isdir, mock_print):
    folder_path = "/fake/dir"
    mock_listdir.return_value = ["species1"]
    mock_isdir.side_effect = lambda x: not x.endswith("sf_files")
    convert_all_species_files(folder_path)
    expected_path = os.path.join(folder_path, "species1", "sf_files")
    expected_message = f"The directory {expected_path} does not exist."
    mock_print.assert_called_with(expected_message)

@patch("rna.data_conversion_helper_functions.convert_quantsf_to_csv.convert_quant_output_to_csv")
@patch("os.path.isdir")
@patch("os.listdir")
def test_convert_all_species_files_successful_conversion(mock_listdir, mock_isdir, mock_convert):
    mock_listdir.side_effect = [["species1"], ["file1.sf", "file2.sf"]]
    mock_isdir.return_value = True
    folder_path = "/fake/dir"
    convert_all_species_files(folder_path)
    input_dir = os.path.join(folder_path, "species1", "sf_files")
    output_dir = os.path.join(folder_path, "species1", "csv_files")
    mock_convert.assert_called_once_with(input_dir, output_dir)

@patch("builtins.print")
@patch("os.path.isdir")
@patch("os.listdir")
def test_convert_all_species_files_no_sf_files_directory(mock_listdir, mock_isdir, mock_print):
    folder_path = "/fake/dir"
    mock_listdir.return_value = ["species1", ".gitignore"]
    mock_isdir.side_effect = lambda x: not x.endswith("sf_files")
    convert_all_species_files(folder_path)
    expected_path = os.path.join(folder_path, "species1", "sf_files")
    mock_print.assert_called_with(f"The directory {expected_path} does not exist.")

@patch("builtins.print")
@patch("os.path.isdir", return_value=True)
@patch("os.listdir")
def test_convert_all_species_files_empty_sf_files_directory(mock_listdir, mock_isdir, mock_print):
    mock_listdir.side_effect = lambda p: ["species1"] if p == "/fake/dir" else []
    folder_path = "/fake/dir"
    convert_all_species_files(folder_path)
    expected_path = os.path.join(folder_path, "species1", "sf_files")
    mock_print.assert_called_with(f"The directory {expected_path} is empty.")

@patch("builtins.print")
@patch("os.path.isfile", return_value=True)
@patch("os.path.isdir", return_value=True)
@patch("os.listdir")
@patch("rna.data_conversion_helper_functions.convert_quantsf_to_csv.convert_quant_output_to_csv", autospec=True)
def test_convert_all_species_files_with_sf_files(mock_convert, mock_listdir, mock_isdir, mock_isfile, mock_print):
    mock_listdir.side_effect = lambda p: ["species1"] if "/fake/dir" in p else ["file1.sf", "file2.sf"]
    folder_path = "/fake/dir"
    convert_all_species_files(folder_path)
    input_dir = os.path.join(folder_path, "species1", "sf_files")
    output_dir = os.path.join(folder_path, "species1", "csv_files")

    expected_calls = [
        call("\nConverting quant files for species: species1"),
        call(f"Data saved to {os.path.normpath(os.path.join(output_dir, 'file1.csv'))}"),
        call(f"Data saved to {os.path.normpath(os.path.join(output_dir, 'file2.csv'))}")
    ]    
    mock_print.assert_has_calls(expected_calls, any_order=True)

@patch("os.listdir")
@patch("os.path.join")
@patch("pandas.read_csv")
@patch("pandas.DataFrame.to_csv")
def test_process_expression_matrix_skips_gitignore(mock_to_csv, mock_read_csv, mock_join, mock_listdir):
    mock_listdir.return_value = ["species1.csv", ".gitignore"]
    mock_join.side_effect = lambda *args: "/".join(args)
    file_path = "/fake/path_to_files"
    output_file_path = "/fake/output_path"
    mock_read_csv.side_effect = lambda file, **kwargs: pd.DataFrame({"transcript_id": [1, 2, 3]}) if "species1.csv" in file else pd.DataFrame()
    process_expression_matrix(file_path, output_file_path)
    mock_read_csv.assert_called_once_with("/fake/path_to_files/species1.csv")
    mock_to_csv.assert_called_once()

@patch("os.listdir")
@patch("os.path.join")
@patch("pandas.read_csv")
@patch("pandas.DataFrame.to_csv")
def test_skip_gitignore_in_processing(mock_to_csv, mock_read_csv, mock_join, mock_listdir):
    mock_listdir.return_value = ["species1.csv", ".gitignore"]
    mock_join.side_effect = lambda *args: "/".join(args)
    file_path = "/fake/path_to_files"
    output_file_path = "/fake/output_path"
    mock_read_csv.side_effect = lambda file, **kwargs: pd.DataFrame({"transcript_id": [1, 2, 3]}) if "species1.csv" in file else None
    process_expression_matrix(file_path, output_file_path)
    calls = [call("/fake/path_to_files/species1.csv")]
    mock_read_csv.assert_has_calls(calls)
    assert mock_read_csv.call_count == 1

def test_convert_quant_output_to_csv():
    sf_data = "gene\tcount\nGene1\t100\nGene2\t200"
    mock_csv_data = [row.split("\t") for row in sf_data.split("\n")[1:]]

    m_open = mock_open(read_data=sf_data)
    mock_writer = MagicMock()

    with patch("os.listdir", return_value=["quant_DRR513083.sf"]), patch(
        "os.path.join", side_effect=lambda *args: "/".join(args)
    ), patch("builtins.open", m_open), patch(
        "csv.reader", return_value=mock_csv_data
    ), patch(
        "csv.writer", return_value=mock_writer
    ):
        convert_quant_output_to_csv("/fake/input", "/fake/output")

        m_open.assert_any_call("/fake/input/quant_DRR513083.sf", "r", encoding="utf-8")
        m_open.assert_any_call(
            "/fake/output/quant_DRR513083.csv", "w", newline="", encoding="utf-8"
        )

        assert mock_writer.writerow.call_count == 2

@patch("os.listdir")
@patch("os.path.isdir")
@patch("pandas.DataFrame.to_csv")
def test_create_expression_matrix_skips_non_directory(mock_to_csv, mock_isdir, mock_listdir):
    mock_isdir.return_value = False
    create_expression_matrix("raw_csv_data_path", "processed_data_path")
    mock_isdir.assert_called_once_with("raw_csv_data_path")
    mock_to_csv.assert_not_called()


@patch("os.listdir")
@patch("os.path.isdir")
@patch("pandas.DataFrame.to_csv")
def test_create_expression_matrix_empty_directory(mock_to_csv, mock_isdir, mock_listdir):
    mock_isdir.return_value = True
    raw_data_path = "/fake/raw_data"
    processed_data_path = "/fake/processed_data"
    def listdir_side_effect(path):
        if path == raw_data_path:
            return ["species1"]  
        elif "species1" in path:
            return []  
        return []
    mock_listdir.side_effect = listdir_side_effect
    create_expression_matrix(raw_data_path, processed_data_path)
    species_csv_path = os.path.join(raw_data_path, "species1", "csv_files")
    mock_listdir.assert_any_call(species_csv_path)  
    mock_to_csv.assert_not_called() 

def test_create_expression_matrix_no_files():
    with patch("os.listdir", return_value=[]) as mock_listdir, patch(
        "os.path.isdir", return_value=True
    ) as mock_isdir, patch("pandas.DataFrame.to_csv") as mock_to_csv:
        create_expression_matrix("raw_data_path", "processed_data_path")
        mock_listdir.assert_called_with("raw_data_path")
        mock_to_csv.assert_not_called()


@patch("os.listdir")
@patch("os.path.isdir")
@patch("pandas.DataFrame.to_csv")
@patch("pandas.read_csv")
def test_create_expression_matrix_single_file(mock_read_csv, mock_to_csv, mock_isdir, mock_listdir):
    species = "species1"
    quant_files = ["quant_DRR513083.csv"]  # Only one file for simplicity
    mock_csv_content = {
        "Name": ["Gene1", "Gene2"],
        "EffectiveLength": [500, 800],
        "TPM": [100, 200],
        "NumReads": [50, 100],
    }
    mock_read_csv.return_value = pd.DataFrame(mock_csv_content)

    # Setup directory structure
    mock_listdir.side_effect = lambda path: {
        "raw_data_path": [species],
        os.path.join("raw_data_path", species): ["csv_files"],
        os.path.join("raw_data_path", species, "csv_files"): quant_files
    }.get(path, [])

    mock_isdir.return_value = True

    create_expression_matrix("raw_data_path", "processed_data_path")

    # Checks
    expected_read_csv_calls = [
        call(os.path.join("raw_data_path", species, "csv_files", "quant_DRR513083.csv"), usecols=['Name', 'TPM']),
        call(os.path.join("raw_data_path", species, "csv_files", "quant_DRR513083.csv"), usecols=['Name', 'EffectiveLength']),
        call(os.path.join("raw_data_path", species, "csv_files", "quant_DRR513083.csv"), usecols=['Name', 'NumReads'])
    ]
    mock_read_csv.assert_has_calls(expected_read_csv_calls, any_order=True)

    # Ensure to_csv was called to save the processed data
    assert mock_to_csv.call_count == 1, "DataFrame.to_csv should have been called once to save the expression matrix."




def test_get_length_scaled_tpm_matrix():
    # Create example DataFrames to use as input
    counts_mat = pd.DataFrame(
        {"Sample1": [100, 200, 300], "Sample2": [150, 250, 350]},
        index=["Gene1", "Gene2", "Gene3"],
    )

    abundance_mat = pd.DataFrame(
        {"Sample1": [10, 20, 30], "Sample2": [15, 25, 35]},
        index=["Gene1", "Gene2", "Gene3"],
    )

    length_mat = pd.DataFrame(
        {"Sample1": [500, 800, 1200], "Sample2": [550, 850, 1250]},
        index=["Gene1", "Gene2", "Gene3"],
    )

    expected_length_scaled_tpm_mat = pd.DataFrame(
        {
            "Sample1": [
                (10 * ((500 + 550) / 2))
                * (
                    (100 + 200 + 300)
                    / (
                        10 * ((500 + 550) / 2)
                        + 20 * ((800 + 850) / 2)
                        + 30 * ((1200 + 1250) / 2)
                    )
                ),
                (20 * ((800 + 850) / 2))
                * (
                    (100 + 200 + 300)
                    / (
                        10 * ((500 + 550) / 2)
                        + 20 * ((800 + 850) / 2)
                        + 30 * ((1200 + 1250) / 2)
                    )
                ),
                (30 * ((1200 + 1250) / 2))
                * (
                    (100 + 200 + 300)
                    / (
                        10 * ((500 + 550) / 2)
                        + 20 * ((800 + 850) / 2)
                        + 30 * ((1200 + 1250) / 2)
                    )
                ),
            ],
            "Sample2": [
                (15 * ((500 + 550) / 2))
                * (
                    (150 + 250 + 350)
                    / (
                        15 * ((500 + 550) / 2)
                        + 25 * ((800 + 850) / 2)
                        + 35 * ((1200 + 1250) / 2)
                    )
                ),
                (25 * ((800 + 850) / 2))
                * (
                    (150 + 250 + 350)
                    / (
                        15 * ((500 + 550) / 2)
                        + 25 * ((800 + 850) / 2)
                        + 35 * ((1200 + 1250) / 2)
                    )
                ),
                (35 * ((1200 + 1250) / 2))
                * (150 + 250 + 350)
                / (
                    15 * ((500 + 550) / 2)
                    + 25 * ((800 + 850) / 2)
                    + 35 * ((1200 + 1250) / 2)
                ),
            ],
        },
        index=["Gene1", "Gene2", "Gene3"],
    )

    # Call the function
    result = get_length_scaled_tpm_matrix(counts_mat, abundance_mat, length_mat)

    # Check the resulting DataFrame
    pd.testing.assert_frame_equal(
        result, expected_length_scaled_tpm_mat, check_dtype=False
    )


def test_calculate_rsd():
    # Create a DataFrame mimicking your actual data structure
    data = {
        "transcript_id": ["gene1", "gene2", "gene3"],
        "DRR513084": [100, 0, 50],
        "DRR513083": [200, 0, 75],
    }
    df = pd.DataFrame(data)

    # Expected DataFrame
    expected_data = {
        "transcript_id": ["gene1", "gene2", "gene3"],
        "DRR513084": [100, 0, 50],
        "DRR513083": [200, 0, 75],
        "mean": [150, 0, 62.5],
        "std_dev": [70.710678, 0, 17.677669],
        "rsd": [(70.710678 / 150), 0, (17.677669 / 62.5)],
    }
    expected_df = pd.DataFrame(expected_data)

    result_df = calculate_rsd(df.copy())

    pd.testing.assert_frame_equal(result_df, expected_df, atol=0.01)


def test_calculate_median_expression():
    data = {
        "transcript_id": ["gene1", "gene2", "gene3"],
        "exp1": [10, 20, 30],
        "exp2": [15, 25, 35],
    }
    df = pd.DataFrame(data)

    expected_data = {
        "transcript_id": ["gene1", "gene2", "gene3"],
        "median_exp": [12.5, 22.5, 32.5],
    }
    expected_df = pd.DataFrame(expected_data)

    result_df = calculate_median_expression(df)

    pd.testing.assert_frame_equal(result_df, expected_df)


def test_process_expression_matrix_no_data():
    with patch("os.listdir", return_value=[]) as mock_listdir, patch(
        "os.path.isdir", side_effect=lambda *args: "/".join(args)
    ), patch("pandas.read_csv") as mock_read_csv, patch(
        "pandas.DataFrame.to_csv"
    ) as mock_to_csv:
        process_expression_matrix("file_path", "output_file_path")

        mock_listdir.assert_called_once_with("file_path")
        mock_read_csv.assert_not_called()
        mock_to_csv.assert_not_called()


@patch("os.listdir")
@patch("os.path.isdir")
@patch("pandas.DataFrame.to_csv")
def test_process_expression_matrix_with_data(mock_to_csv, mock_isdir, mock_listdir):
    species_files = ["species1.csv", "species2.csv", ".gitignore"]
    mock_expression_data = pd.DataFrame(
        {
            "Name": ["Gene1", "Gene2", "Gene3"],
            "TPM1": [100, 200, 300],
            "TPM2": [150, 250, 350],
        }
    )
    expected_filtered_data = mock_expression_data.loc[[0, 1]]
    median_expression_data = pd.DataFrame({"MedianTPM": [125, 225]})
    with patch("os.listdir", return_value=species_files) as mock_listdir, patch(
        "os.path.join", side_effect=lambda *args: "/".join(args)
    ), patch(
        "pandas.read_csv", return_value=mock_expression_data
    ) as mock_read_csv, patch(
        "pandas.DataFrame.to_csv"
    ) as mock_to_csv, patch(
        "rna.data_conversion_helper_functions.process_expression_matrix.calculate_rsd",
        return_value=pd.DataFrame({"rsd": [1, 1, 3]}),
    ), patch(
        "rna.data_conversion_helper_functions.process_expression_matrix.calculate_median_expression",
        return_value=median_expression_data,
    ):
        process_expression_matrix("file_path", "output_file_path")
        mock_read_csv.assert_any_call(
            "file_path/species1.csv"
        )
        mock_read_csv.assert_any_call(
            "file_path/species2.csv"
        )
        assert ".gitignore" not in [call.args[0] for call in mock_read_csv.call_args_list]
        assert mock_read_csv.call_count == 2  
        assert mock_to_csv.call_count == 2
        mock_to_csv.assert_called_with(
            "output_file_path/rna_expression_species2.csv", index=False
        )


@patch("os.walk")
def test_list_files(mock_walk):
    # Setup the mock to simulate os.walk behavior
    mock_walk.return_value = [
        ("/fake/dir", ("subdir",), ("file1.txt", "file2.txt")),
        ("/fake/dir/subdir", (), ("file3.txt",))
    ]

    # Create expected files list with normalized paths to ensure OS compatibility
    expected_files = [
        os.path.normpath(os.path.join("/fake/dir", "file1.txt")),
        os.path.normpath(os.path.join("/fake/dir", "file2.txt")),
        os.path.normpath(os.path.join("/fake/dir", "subdir", "file3.txt")),
    ]

    # Call the function to be tested
    result = list_files("/fake/dir")

    # Normalize all paths in the result for comparison
    normalized_result = [os.path.normpath(path) for path in result]

    # Assert that the normalized result matches the expected normalized files list
    assert normalized_result == expected_files, f"Expected {expected_files}, got {normalized_result}"

    # Verify that os.walk was called correctly
    mock_walk.assert_called_once_with("/fake/dir")





def test_create_samplesheet_for_one_species():
    fake_files = [
        "/path/to/species/sample1_1.fastq.gz",
        "/path/to/species/sample1_2.fastq.gz",
        "/path/to/species/sample2_1.fastq.gz",
    ]

    with patch(
        "rna.data_conversion_helper_functions.create_samplesheet_csv.list_files",
        return_value=fake_files,
    ), patch("builtins.open", mock_open()) as mocked_file, patch(
        "csv.writer"
    ) as mock_csv_writer:

        create_samplesheet_for_one_species(
            species_name="homo_sapiens",
            local_dir_path_with_fastq_files_for_one_species="/path/to/species",
            local_dir_path_to_save_samplesheets="/path/to/save",
        )

        mocked_file.assert_called_once_with(
            "/path/to/save/homo_sapiens_samplesheet.csv", "w", encoding="utf-8"
        )

        mock_csv_writer_instance = mock_csv_writer.return_value
        mock_csv_writer_instance.writerow.assert_called()
        assert mock_csv_writer_instance.writerows.call_count == 1


@patch("os.makedirs")
def test_create_directories_for_species(mock_makedirs):
    species_data = {"Homo sapiens": 9606, "Mus musculus": 10090}
    base_directory = "/fakepath/data"
    create_directories_for_species(species_data, base_directory)
    expected_calls = [
        call(os.path.join(base_directory, "homo_sapiens"), exist_ok=True),
        call(os.path.join(base_directory, "homo_sapiens", "sf_files"), exist_ok=True),
        call(os.path.join(base_directory, "homo_sapiens", "csv_files"), exist_ok=True),
        call(os.path.join(base_directory, "mus_musculus"), exist_ok=True),
        call(os.path.join(base_directory, "mus_musculus", "sf_files"), exist_ok=True),
        call(os.path.join(base_directory, "mus_musculus", "csv_files"), exist_ok=True),
    ]
    mock_makedirs.assert_has_calls(expected_calls, any_order=True)

