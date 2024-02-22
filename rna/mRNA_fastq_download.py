
import subprocess
import os
import pandas as pd
from pysradb import SRAweb

# Function to download SRA data
def download_sra_data(csv_file_path, output_directory, limit=1):
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
        # if download_count >= limit:
        #     print(f"Reached download limit of {limit}.")
        #     break 

        srr_id = row['srr_id'] 

        species_name = 'Chlamydomonas reinhardtii'

        if row['species'] == species_name: # and srr_id == 'SRR26129966':

            try:
                # Download using the fasterq-dump command for each SRR ID (construct as a list)
                command = ['fasterq-dump', srr_id, '--outdir', output_directory]
                subprocess.run(command, check=True)
                print(f"SRR ID {srr_id} downloaded to {output_directory}")

                download_count += 1

            except Exception as e:
                print(f"Error downloading SRR ID {srr_id}: {e}")
                #breakpoint()

# Main execution
if __name__ == "__main__":

    # Call CSV file path returned by the 'query_and_csv_production' file
    csv_file_path = '/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/output_srx_srr.csv'  

    # Output dir here
    output_directory = '/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/draft_folder_for_rnaseq/input_dir/Chlamydomonas_reinhardtii/fasta'

    download_sra_data(csv_file_path, output_directory)
