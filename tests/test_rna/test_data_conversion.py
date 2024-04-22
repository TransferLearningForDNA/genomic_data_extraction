import pytest
from unittest.mock import patch, MagicMock, mock_open
import csv
import pandas as pd
from rna.data_conversion_helper_functions.convert_quantsf_to_csv import convert_all_species_files, \
    convert_quant_output_to_csv
from rna.data_conversion_helper_functions.create_expression_matrix import create_expression_matrix, \
    get_length_scaled_tpm_matrix
from rna.data_conversion_helper_functions.process_expression_matrix import process_expression_matrix, \
    calculate_median_expression, calculate_rsd


@patch('builtins.print')
@patch('os.path.isdir')
@patch('os.listdir')
def test_convert_all_species_files_no_directory(mock_listdir, mock_isdir, mock_print):
    mock_listdir.return_value = ['species1']
    mock_isdir.side_effect = lambda x: x.endswith('species1')
    convert_all_species_files("/fake/dir")
    mock_print.assert_called_with("The directory /fake/dir/species1/sf_files does not exist.")


@patch('rna.data_conversion_helper_functions.convert_quantsf_to_csv.convert_quant_output_to_csv')
@patch('os.path.isdir')
@patch('os.listdir')
def test_convert_all_species_files_successful_conversion(mock_listdir, mock_isdir, mock_convert):
    mock_listdir.side_effect = [['species1'], ['file1.sf', 'file2.sf']]  # species1 exists, and has sf files
    mock_isdir.side_effect = lambda x: 'sf_files' in x or 'species1' in x

    convert_all_species_files("/fake/dir")
    mock_convert.assert_called_once_with("/fake/dir/species1/sf_files", "/fake/dir/species1/csv_files")


def test_convert_quant_output_to_csv():
    sf_data = "gene\tcount\nGene1\t100\nGene2\t200"
    mock_csv_data = [row.split('\t') for row in sf_data.split('\n')[1:]]

    m_open = mock_open(read_data=sf_data)
    mock_writer = MagicMock()

    with patch('os.listdir', return_value=['quant_DRR513083.sf']), \
            patch('os.path.join', side_effect=lambda *args: '/'.join(args)), \
            patch('builtins.open', m_open), \
            patch('csv.reader', return_value=mock_csv_data), \
            patch('csv.writer', return_value=mock_writer):
        convert_quant_output_to_csv('/fake/input', '/fake/output')

        m_open.assert_any_call('/fake/input/quant_DRR513083.sf', 'r', encoding='utf-8')
        m_open.assert_any_call('/fake/output/quant_DRR513083.csv', 'w', newline='', encoding='utf-8')

        assert mock_writer.writerow.call_count == 2


def test_create_expression_matrix_no_files():
    with patch('os.listdir', return_value=[]) as mock_listdir, \
            patch('os.path.isdir', return_value=True) as mock_isdir, \
            patch('pandas.DataFrame.to_csv') as mock_to_csv:
        create_expression_matrix("raw_data_path", "processed_data_path")
        mock_listdir.assert_called_with("raw_data_path")
        mock_to_csv.assert_not_called()


def test_create_expression_matrix_single_file():
    species = 'species1'
    quant_file = 'quant_DRR513083.csv'
    mock_csv_content = {
        'Name': ['Gene1', 'Gene2'],
        'EffectiveLength': [500, 800],
        'TPM': [100, 200],
        'NumReads': [50, 100]
    }

    def listdir_side_effect(path):
        if "csv_files" in path:
            return [quant_file]
        elif "raw_data_path" in path:
            return [species]
        return []

    with patch('os.listdir', side_effect=listdir_side_effect) as mock_listdir, \
            patch('os.path.isdir', return_value=True) as mock_isdir, \
            patch('pandas.read_csv', return_value=pd.DataFrame(mock_csv_content)) as mock_read_csv, \
            patch('pandas.DataFrame.to_csv') as mock_to_csv:

        create_expression_matrix("raw_data_path", "processed_data_path")

        mock_listdir.assert_any_call("raw_data_path")
        mock_listdir.assert_any_call(f"raw_data_path/{species}/csv_files")

        mock_read_csv.assert_called()
        mock_to_csv.assert_called()

        mock_read_csv.assert_called_with(f"raw_data_path/{species}/csv_files/{quant_file}",
                                         usecols=["Name", "NumReads"])

        assert mock_read_csv.call_count == 3
        assert mock_to_csv.call_count == 1


def test_get_length_scaled_tpm_matrix():
    # Create example DataFrames to use as input
    counts_mat = pd.DataFrame({
        'Sample1': [100, 200, 300],
        'Sample2': [150, 250, 350]
    }, index=['Gene1', 'Gene2', 'Gene3'])

    abundance_mat = pd.DataFrame({
        'Sample1': [10, 20, 30],
        'Sample2': [15, 25, 35]
    }, index=['Gene1', 'Gene2', 'Gene3'])

    length_mat = pd.DataFrame({
        'Sample1': [500, 800, 1200],
        'Sample2': [550, 850, 1250]
    }, index=['Gene1', 'Gene2', 'Gene3'])

    expected_length_scaled_tpm_mat = pd.DataFrame({
        'Sample1': [(10 * ((500 + 550) / 2)) * ((100 + 200 + 300) / (10 * ((500 + 550) / 2) +
                                                                     20 * ((800 + 850) / 2) +
                                                                     30 * ((1200 + 1250) / 2))),
                    (20 * ((800 + 850) / 2)) * ((100 + 200 + 300) / (10 * ((500 + 550) / 2) +
                                                                     20 * ((800 + 850) / 2) +
                                                                     30 * ((1200 + 1250) / 2))),
                    (30 * ((1200 + 1250) / 2)) * ((100 + 200 + 300) / (10 * ((500 + 550) / 2) +
                                                                       20 * ((800 + 850) / 2) +
                                                                       30 * ((1200 + 1250) / 2)))],
        'Sample2': [(15 * ((500 + 550) / 2)) * ((150 + 250 + 350) / (15 * ((500 + 550) / 2) +
                                                                     25 * ((800 + 850) / 2) +
                                                                     35 * ((1200 + 1250) / 2))),
                    (25 * ((800 + 850) / 2)) * ((150 + 250 + 350) / (15 * ((500 + 550) / 2) +
                                                                     25 * ((800 + 850) / 2) +
                                                                     35 * ((1200 + 1250) / 2))),
                    (35 * ((1200 + 1250) / 2)) * (150 + 250 + 350) / (15 * ((500 + 550) / 2) +
                                                                      25 * ((800 + 850) / 2) +
                                                                      35 * ((1200 + 1250) / 2))]
    }, index=['Gene1', 'Gene2', 'Gene3'])

    # Call the function
    result = get_length_scaled_tpm_matrix(counts_mat, abundance_mat, length_mat)

    # Check the resulting DataFrame
    pd.testing.assert_frame_equal(result, expected_length_scaled_tpm_mat, check_dtype=False)


# def test_calculate_rsd():
#     data = {
#         'transcript_id': ['gene1', 'gene2', 'gene3'],
#         'exp1': [100, 0, 50],
#         'exp2': [200, 0, 75],
#
#     }
#     # df = pd.DataFrame(data).set_index('transcript_id')
#     # df = pd.DataFrame(data, index=['gene1', 'gene2', 'gene3'])
#     df = pd.DataFrame(data)
#     # df.set_index('transcript_id', inplace=True)
#
#     print(df)
#
#     # Expected DataFrame
#     expected_data = {
#         'transcript_id': ['gene1', 'gene2', 'gene3'],
#         'exp1': [100, 0, 50],
#         'exp2': [200, 0, 75],
#         'mean': [150, 0, 62.5],
#         'std_dev': [50, 0, 12.5],
#         'rsd': [(50 / 150), 0, (12.5 / 62.5)]
#     }
#     # expected_df = pd.DataFrame(expected_data).set_index(df.index)
#     # expected_df = pd.DataFrame(expected_data, index=['gene1', 'gene2', 'gene3'])
#
#     expected_df = pd.DataFrame(expected_data)
#     # expected_df.set_index(pd.Index(['gene1', 'gene2', 'gene3']), inplace=True)
#
#     result_df = calculate_rsd(df.copy())
#
#     print(result_df)
#
#     pd.testing.assert_frame_equal(result_df, expected_df, check_dtype=True)

def test_calculate_median_expression():
    data = {
        'transcript_id': ['gene1', 'gene2', 'gene3'],
        'exp1': [10, 20, 30],
        'exp2': [15, 25, 35]
    }
    df = pd.DataFrame(data)

    expected_data = {
        'transcript_id': ['gene1', 'gene2', 'gene3'],
        'median_exp': [12.5, 22.5, 32.5]
    }
    expected_df = pd.DataFrame(expected_data)

    result_df = calculate_median_expression(df)

    pd.testing.assert_frame_equal(result_df, expected_df)

def test_process_expression_matrix_no_data():
    with patch('os.listdir', return_value=[]) as mock_listdir, \
            patch('os.path.isdir', side_effect=lambda *args: "/".join(args)), \
            patch('pandas.read_csv') as mock_read_csv, \
            patch('pandas.DataFrame.to_csv') as mock_to_csv:
        process_expression_matrix("file_path", "output_file_path")

        mock_listdir.assert_called_once_with("file_path")
        mock_read_csv.assert_not_called()
        mock_to_csv.assert_not_called()


def test_process_expression_matrix_with_data():
    species_files = ['species1.csv', 'species2.csv']
    mock_expression_data = pd.DataFrame({
        'Name': ['Gene1', 'Gene2', 'Gene3'],
        'TPM1': [100, 200, 300],
        'TPM2': [150, 250, 350]
    })
    expected_filtered_data = mock_expression_data.loc[[0, 1]]
    median_expression_data = pd.DataFrame({'MedianTPM': [125, 225]})

    with patch('os.listdir', return_value=species_files) as mock_listdir, \
            patch('os.path.join', side_effect=lambda *args: "/".join(args)), \
            patch('pandas.read_csv', return_value=mock_expression_data) as mock_read_csv, \
            patch('pandas.DataFrame.to_csv') as mock_to_csv, \
            patch('rna.data_conversion_helper_functions.process_expression_matrix.calculate_rsd',
                  return_value=pd.DataFrame({'rsd': [1, 1, 3]})), \
            patch('rna.data_conversion_helper_functions.process_expression_matrix.calculate_median_expression',
                  return_value=median_expression_data):
        process_expression_matrix("file_path", "output_file_path")

        assert mock_read_csv.call_count == len(species_files)
        assert mock_to_csv.call_count == len(species_files)
        mock_to_csv.assert_called_with("output_file_path/rna_expression_species2.csv", index=False)
