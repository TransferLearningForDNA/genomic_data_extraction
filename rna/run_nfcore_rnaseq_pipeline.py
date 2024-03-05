import subprocess

# Run the pipeline given a samplesheet csv file (one species at a time)

# define the variables for the parameters
sample_sheet_path = '/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/draft_folder_for_rnaseq/csv_dir/samplesheet.csv'  # better as an input requested from user? (input())
assert sample_sheet_path.endswith('csv')  # check file format

path_to_outputs = '/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/draft_folder_for_rnaseq/rnaseq_output_dir'

# define your command and arguments
command = ['nextflow', 'run', 'nf-core/rnaseq',
           '-params-file', 'rnaseq_params.yaml']

# run the pipeline
result = subprocess.run(command, capture_output=True, text=True)

print(result.stdout)  # print the output on the terminal
