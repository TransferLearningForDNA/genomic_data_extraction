import os
import csv

# TODO: specify the path to the folder containing the sample fastq files
# folder_path = '/path/to/your/folder'  # if saved in a local directory
folder_path = ''  # if saved in Google Drive OR Imperial OneDrive (#TODO)


# list all the files in the folder path with a fastq extension (sanity check)
file_extension = '.fastq'
files = [file for file in os.listdir(folder_path) if file.endswith(file_extension)]

# QUESTION 2
# option 1: preprocess all samples across all our species (one csv file)
# OR
# option 2: preprocess samples within each species separately (multiple csv files)
# comment: is it fine/appropriate to preprocess (all samples of) every species in one go in the pipeline (i.e., option 1)
# BELOW: CODE LOGIC FOR OPTION 1

# iterate over the fastq files to populate the dict containing the fastq filepath(s)
# of each sample (across all species we are considering/saved in the folder)
sample_fastq_files_path_dict = dict()
for sample_fastq_file in files:

    # get the absolute file path
    file_path = os.path.join(folder_path, sample_fastq_file)

    sample_name_key = sample_fastq_file[:-8]  # naming convention = samplename_1.fastq

    if sample_name_key in sample_fastq_files_path_dict:
        sample_fastq_files_path_dict[sample_name_key].append(file_path)
        # sort by fastq file number
        sample_fastq_files_path_dict[sample_name_key] = sorted(
            sample_fastq_files_path_dict[sample_name_key],
            key=lambda fastq_filename: fastq_filename[-7]
        )
    else:
        sample_fastq_files_path_dict[sample_name_key] = [file_path]

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
