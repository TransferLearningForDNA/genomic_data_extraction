import os
import csv

# list all the files in the LOCAL folder path:
# assuming we have downloaded the files from Onedrive first
def list_files(directory):
    file_paths = []
    # Walk through all files and subdirectories in the specified directory
    for root, _, files in os.walk(directory):
        for file_name in files:
            # Get the full path of each file
            file_path = os.path.join(root, file_name)
            # Append the file path to the list
            file_paths.append(file_path)
    return file_paths

# Specify the directory path
directory_path = "/path/to/your/directory"

# Retrieve the list of file paths
file_paths = list_files(directory_path)

# preprocess all samples across all our species (one csv file)
# TODO: update this to be one csv file PER species

# iterate over the fastq files to populate the dict containing the fastq filepath(s)
# of each sample (across all species we are considering/saved in the folder)
sample_fastq_files_path_dict = dict()
for sample_fastq_file_path in file_paths:

    sample_name_key = sample_fastq_file_path[:-8]  # naming convention = samplename_1.fastq

    if sample_name_key in sample_fastq_files_path_dict:
        sample_fastq_files_path_dict[sample_name_key].append(sample_fastq_file_path)
        # sort by fastq file number
        sample_fastq_files_path_dict[sample_name_key] = sorted(
            sample_fastq_files_path_dict[sample_name_key],
            key=lambda fastq_filename: fastq_filename[-7]
        )
    else:
        sample_fastq_files_path_dict[sample_name_key] = [sample_fastq_file_path]

# populate the data structure that will hold the rows of the csv file
strandedness = 'auto'  # using default parameter value for now
data = []   # list of sublists (where each sublist is a sample/row in the dataset)
for sample_name, fastq_files_paths_list in sample_fastq_files_path_dict:

    if len(fastq_files_paths_list) == 1:
        fastq_file1_path = fastq_files_paths_list[0]
        fastq_file2_path = ''
    else:
        assert len(fastq_files_paths_list) == 2  # max number of fastq files per sample
        fastq_file1_path = fastq_files_paths_list[0]
        fastq_file2_path = fastq_files_paths_list[1]

    sample_row_data = [sample_name, fastq_file1_path, fastq_file2_path, strandedness]
    data.append(sample_row_data)

# create the samplesheet csv file (input to the nextflow nfcore/rnaseq pipeline)
# columns of the samplesheet csv file
header = ['sample', 'fastq_1', 'fastq_2', 'strandedness']
with open("samplesheet.csv", "w") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)
    writer.writerows(data)