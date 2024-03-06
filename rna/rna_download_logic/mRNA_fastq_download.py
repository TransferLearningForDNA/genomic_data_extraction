
import subprocess
import os
import datetime
import pandas as pd
from pysradb import SRAweb

# Function to download SRA data
def download_sra_data(csv_file_path, output_directory, limit=10):
    """This is a function to download SRA data from the CSV file returned by the 'query_and_csv_production' file. This is done using the fasterq-dump command. 
    
    NOTE: Be wary here with 2 things:

    1. SRA-toolkit installation - make sure you have the correct version installed in your environment, ad otherwise faster-q may raise errors;

    2. The download limit parameter - while we originally planned to have 50 returned, this has now been set to 1, as the files are very very large in size <15GB per run. It can take a long time and use a lot of memory, so be careful with this parameter."""
    
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    db = SRAweb()
    download_count = 0

    for index, row in df.iterrows():
        if download_count >= limit:
            print(f"Reached download limit of {limit}.")
            break 

        srr_id = row['srr_id'] 
        species_name = 'Chlamydomonas reinhardtii'
        
        # check that the fasta files have not already been downloaded
        # for this sample (i.e. SRR ID)
        output_file = os.path.join(output_directory, f"{srr_id}_1.fastq")
        compressed_output_file = os.path.join(output_directory, f"{srr_id}_1.fastq.gz")

        if row['species'] == species_name and (not os.path.exists(output_file)) and (not os.path.exists(compressed_output_file)) :
            try:
                print(f"Starting download of SRR ID {srr_id} at {datetime.datetime.now()}", flush=True)
                # Download using the fasterq-dump command for each SRR ID (construct as a list)
                command = ['fasterq-dump', srr_id, '--outdir', output_directory]
                subprocess.run(command, check=True)

                print(f"SRR ID {srr_id} downloaded to {output_directory} at {datetime.datetime.now()}", flush=True)

                download_count += 1

                # list files in the output directory after each download
                print(f"Files in {output_directory} after download:")
                print(os.listdir(output_directory))

            except Exception as e:
                print(f"Error downloading SRR ID {srr_id}: {e}", flush=True)
                #breakpoint()

# Main execution
if __name__ == "__main__":

    # Call CSV file path returned by the 'query_and_csv_production' file
    csv_file_path = '/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/output_srx_srr.csv'  

    # Output dir here
    output_directory = '/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/rnaseq/input_dir/Chlamydomonas_reinhardtii/fasta'

    download_sra_data(csv_file_path, output_directory)
