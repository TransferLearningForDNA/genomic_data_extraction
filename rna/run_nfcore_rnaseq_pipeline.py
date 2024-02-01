import subprocess

# define the variables for the parameters
sample_sheet_path = 'samplesheet.csv'  # better as an input requested from user? (input())
assert sample_sheet_path.endswith('csv')  # check file format

path_to_outputs = 'TODO'
genome_wanted = 'TODO'  # do we need this parameter?

# define your command and arguments
command = ['nextflow', 'run', 'nf-core/rnaseq',
           '--input', sample_sheet_path,
           '--outdir', path_to_outputs,
           '--genome', genome_wanted,  # optional (double-check)
           '-profile', 'docker']  # or try without profile flag first

# run the pipeline
result = subprocess.run(command, capture_output=True, text=True)

print(result.stdout)  # print the output on the terminal
