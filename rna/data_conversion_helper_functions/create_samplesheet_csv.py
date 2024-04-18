import os
import csv
from typing import List


# Assumptions: we have downloaded the fastq files from Onedrive.


def list_files(directory: str) -> List[str]:
    """Lists all the files in a local directory.

    Args:
        directory (str): The path to the folder containing files.

    Returns:
        List[str]: A list of file paths.
    """
    file_paths = []

    # go through all files and subdirectories in the specified directory
    for root, _, files in os.walk(directory):
        for file_name in files:
            # get the full path of each file
            file_path = os.path.join(root, file_name)

            # store the file path
            file_paths.append(file_path)

    return file_paths


def create_samplesheet_for_one_species(
    species_name: str,
    local_dir_path_with_fastq_files_for_one_species: str,
    local_dir_path_to_save_samplesheets: str,
) -> None:
    """Create a samplesheet csv file for a species (input to the nf-core/rna-seq pipeline).

    Args:
        species_name (str): name of the species that we are creating the samplesheet
            csv file for. This will be used in the name of the csv file created.
        local_dir_path_with_fastq_files_for_one_species (str): path to the local
            directory containing the fastq files for the species.
        local_dir_path_to_save_samplesheets (str): path to a local directory to
            use for saving the samplesheet csv files of all species.

    Returns:
        None: This function does not return a value but outputs files to the specified directory.
    """
    # Retrieve the list of file paths
    file_paths = list_files(local_dir_path_with_fastq_files_for_one_species)

    # iterate over the fastq files to populate the dict containing the fastq filepath(s) of each sample
    sample_fastq_files_path_dict = {}
    for sample_fastq_file_path in file_paths:

        sample_filename = os.path.basename(
            sample_fastq_file_path
        )  # naming convention = samplename_1.fastq.gz
        sample_name_key = sample_filename.split("_")[0]

        if sample_name_key != ".DS":  # file in macOS

            if sample_name_key in sample_fastq_files_path_dict:
                sample_fastq_files_path_dict[sample_name_key].append(
                    sample_fastq_file_path
                )
                # sort by fastq file number
                sample_fastq_files_path_dict[sample_name_key] = sorted(
                    sample_fastq_files_path_dict[sample_name_key],
                    key=lambda fastq_filename: fastq_filename[-10],
                )
            else:
                sample_fastq_files_path_dict[sample_name_key] = [sample_fastq_file_path]

    # populate the data structure that will hold the rows of the csv file
    strandedness = "auto"  # using default parameter value for now
    data = []  # list of sublists (where each sublist is a sample/row in the dataset)
    for sample_name, fastq_files_paths_list in sample_fastq_files_path_dict.items():

        if len(fastq_files_paths_list) == 1:
            fastq_file1_path = fastq_files_paths_list[0]
            fastq_file2_path = ""
        else:
            assert (
                len(fastq_files_paths_list) == 2
            )  # max number of fastq files per sample
            fastq_file1_path = fastq_files_paths_list[0]
            fastq_file2_path = fastq_files_paths_list[1]

        sample_row_data = [
            sample_name,
            fastq_file1_path,
            fastq_file2_path,
            strandedness,
        ]
        data.append(sample_row_data)

    # create the samplesheet csv file (input to the nextflow nfcore/rnaseq pipeline)
    # columns of the samplesheet csv file
    header = ["sample", "fastq_1", "fastq_2", "strandedness"]
    with open(
        f"{local_dir_path_to_save_samplesheets}/{species_name}_samplesheet.csv",
        "w",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(data)


if __name__ == "__main__":
    local_dir_path_to_save_samplesheets = (
        "/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/rnaseq/csv_dir"
    )
    # species_names = ['species1', 'species2', 'species3']
    # for species_name in species_names:

    #     local_dir_path_with_fastq_files_for_one_species = "/path/to/your/input/directory"

    #     create_samplesheet_for_one_species(species_name,
    #                                     local_dir_path_with_fastq_files_for_one_species,
    #                                     local_dir_path_to_save_samplesheets)

    species = "Chlamydomonas_reinhardtii"
    local_dir_path_with_fastq_files_for_one_species = "/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/rnaseq/input_dir/Chlamydomonas_reinhardtii/fasta"
    create_samplesheet_for_one_species(
        species,
        local_dir_path_with_fastq_files_for_one_species,
        local_dir_path_to_save_samplesheets,
    )
