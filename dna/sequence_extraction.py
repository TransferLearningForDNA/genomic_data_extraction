""" Extract DNA sequences from fasta and gff files.

geneID, Promoter, 5'UTR, CDS, 3'UTR, Terminator
"""

import subprocess
import csv


def extract_sequences(species, taxid):
    gff_file = f"dna/ncbi_datasets/{species}/genomic.gff"
    fasta_file = f"dna/ncbi_datasets/{species}/genomic.fna"

    # Path to the Perl script
    perl_script_path = 'AGAT/bin/agat_sp_extract_sequences.pl'
    # perl_script_path = 'AGAT/bin/agat_sp_extract_attributes.pl'

    command_cds = [perl_script_path, "-gff", gff_file, "-fasta", fasta_file, "-t", "cds", "-o", "output_cds.fna"]
    command_utr5 = [perl_script_path, "-gff", gff_file, "-fasta", fasta_file, "-t", "five_prime_utr", "-o", "output_utr5.fna"]
    # command_utr3 = [perl_script_path, "-gff", gff_file, "-fasta", fasta_file, "-t", "utr3", "-o", "output_utr3.fna"]
    # command_promoter = [perl_script_path, "-gff", gff_file, "-fasta", fasta_file, "-t", "gene", "--upstream", "1000",
    #                     "-o", "output_prom.fna"]
    # command_terminator = [perl_script_path, "-gff", gff_file, "-fasta", fasta_file, "-t", "gene", "--downstream", "500",
    #                       "-o", "output_term.fna"]

    # command = [perl_script_path, "-gff", gff_file, "-att", "gene_id", "-o", "output.txt"]

    result = subprocess.run(command_cds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        cds = result.stdout
        # with open('output.txt', 'w') as f:
        #     f.write(cds)
    else:
        print("Error:", result.stderr)

    # Assuming output_data is a string with your data
    # data_lines = cds.split('\n')  # Split the data into lines
    #
    # # Open a file in write mode
    # with open('cds.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #
    #     # Write each line to the CSV
    #     for line in data_lines:
    #         writer.writerow([line])


if __name__ == "__main__":
    species = "osterococcus_tauri"
    taxid = "70448"
    extract_sequences(species, taxid)

