import csv
import os


def convert_quant_output_to_csv(input_file_path, output_file_path):
    """ Convert quantification file, Salmon (nf-core rna-seq) output, to a csv file.

    Args:
        input_file_path (str): quant.sf file path (tsv: tab-separated values)
        output_file_path (str): file path to store the csv version of the quant file
    """
    with open(input_file_path, 'r') as input_file, open(output_file_path, 'w', newline='') as output_file:
        # Create a csv reader object to read from the tsv file (tab-delimited)
        # TODO check delimiter works \t with original quant output
        tsv_reader = csv.reader(input_file, delimiter='\t')

        # Create a csv writer object to write to the csv file (comma-delimited)
        csv_writer = csv.writer(output_file)

        # Loop through each row in the input file and write it to the output file
        for row in tsv_reader:
            csv_row = list(row[0].split('   '))
            csv_writer.writerow(csv_row)

    # print(f'Converted {input_file_path} to {output_file_path} successfully.')


if __name__ == "__main__":
    # Path to input quant.sf file
    quant_file_path = 'quant_test.sf'
    # Path to output CSV file
    output_csv_path = 'quant_test.csv'
    # Convert quantification file from .sf (Salmon output file) to csv
    convert_quant_output_to_csv(quant_file_path, output_csv_path)
