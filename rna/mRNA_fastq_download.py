
import subprocess
import os
import pandas as pd
from pysradb import SRAweb


# Was having download location issues (have modified to raw string
# format even though it shouldn't really be an issue...)
def download_sra_data(csv_file_path, output_directory, limit=1):
    
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

        try:
            # Download using the fasterq-dump command for each SRR ID (construct as a list)
            command = ['fasterq-dump', srr_id, '--outdir', output_directory]
            subprocess.run(command, check=True)
            print(f"SRR ID {srr_id} downloaded to {output_directory}")

            download_count += 1

        except Exception as e:
            print(f"Error downloading SRR ID {srr_id}: {e}")
            breakpoint()

# Main execution
if __name__ == "__main__":
    # CSV file path
    csv_file_path = 'output_srx_srr_1.csv'  
    # Output dir here
    output_directory = '/Users/meghoward/Documents/Imperial MSc/Term_2/Phycoworks/genomic_data_extraction/rna/fastq_files'
    download_sra_data(csv_file_path, output_directory)
