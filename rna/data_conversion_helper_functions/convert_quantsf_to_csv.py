import os
import csv


def convert_all_species_files(folder_path: str) -> None:
    """Convert quantification files from sf to csv for each species.

    Args:
        folder_path (str) : Path to raw quant files folder.

    Returns:
        None: This function does not return a value but outputs files to the specified directory.
    """
    # Iterate over items in the directory
    for item in os.listdir(folder_path):
        if item == ".gitignore":
            continue
        item_path = os.path.join(folder_path, item)  # Get the full path of the item
        if os.path.isdir(item_path):  # Check if the item is a directory
            print(f"\nConverting quant files for species: {item}")

            # Check if the directory containing sf files exists
            sf_files_path = os.path.join(item_path, "sf_files")
            if not os.path.isdir(sf_files_path):
                print(f"The directory {sf_files_path} does not exist.")
            elif not os.listdir(sf_files_path):
                print(f"The directory {sf_files_path} is empty.")
            else:
                csv_files_path = os.path.join(
                    item_path, "csv_files"
                )  # path to store csv files
                # Convert all quant sf files to csv
                convert_quant_output_to_csv(sf_files_path, csv_files_path)


def convert_quant_output_to_csv(input_path: str, output_path: str) -> None:
    """Convert quantification files, Salmon (nf-core rna-seq) output, to csv files.

    Args:
        input_path (str): Folder path containing quant_DRR513083.sf files (TSV: tab-separated values).
        output_path (str): Folder path to store the CSV version of the quant files.

    Returns:
        None: This function does not return a value but outputs files to the specified directory.
    """
    # Iterate over files in the directory
    for filename in os.listdir(input_path):
        if filename.endswith(".sf"):
            input_file_path = os.path.join(input_path, filename)
            output_file_path = os.path.join(
                output_path, filename.replace(".sf", ".csv")
            )

            with open(input_file_path, "r", encoding="utf-8") as input_file, open(
                output_file_path, "w", newline="", encoding="utf-8"
            ) as output_file:
                tsv_reader = csv.reader(input_file, delimiter="\t")
                csv_writer = csv.writer(output_file)

                for row in tsv_reader:
                    csv_writer.writerow(row)


if __name__ == "__main__":
    # Path to input raw quant.sf files folder
    raw_quant_path = "quant_files/raw"
    convert_all_species_files(raw_quant_path)
