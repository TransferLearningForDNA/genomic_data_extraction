import csv
import os


def convert_all_species_files(folder_path):
    """ Convert quantification files from sf to csv for each species."""

    # Iterate over items in the directory
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)  # Get the full path of the item
        if os.path.isdir(item_path):  # Check if the item is a directory
            print(f"\nConverting quant files for species: {item}")

            # Check if the directory containing sf files exists
            sf_files_path = os.path.join(item_path, 'sf_files')
            if not os.path.isdir(sf_files_path):
                print(f"The directory {sf_files_path} does not exist.")
            elif not os.listdir(sf_files_path):
                print(f"The directory {sf_files_path} is empty.")
            else:
                csv_files_path = os.path.join(item_path, 'csv_files')  # path to store csv files
                # Convert all quant sf files to csv
                convert_quant_output_to_csv(sf_files_path, csv_files_path)


def convert_quant_output_to_csv(input_path, output_path):
    """ Convert quantification files, Salmon (nf-core rna-seq) output, to a csv files.

    Args:
        input_path (str): quant_DRR513083.sf files folder path (tsv: tab-separated values)
        output_path (str): folder path to store the csv version of the quant files
    """
    # Iterate over files in the directory
    for filename in os.listdir(input_path):
        if filename.endswith(".sf"):
            input_file_path = os.path.join(input_path, filename)
            output_file_path = os.path.join(output_path, filename.replace('.sf', '.csv'))

            with open(input_file_path, 'r') as input_file, open(output_file_path, 'w', newline='') as output_file:
                # Create a csv reader object to read from the tsv file (tab-delimited)
                tsv_reader = csv.reader(input_file, delimiter='\t')

                # Create a csv writer object to write to the csv file (comma-delimited)
                csv_writer = csv.writer(output_file)

                # Loop through each row in the input file and write it to the output file
                for row in tsv_reader:
                    csv_writer.writerow(row)


if __name__ == "__main__":
    # Path to input raw quant.sf files folder
    raw_quant_path = 'quant_files/raw'
    convert_all_species_files(raw_quant_path)
