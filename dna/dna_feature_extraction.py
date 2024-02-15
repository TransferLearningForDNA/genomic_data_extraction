import os
import csv
import tempfile
import shutil
from itertools import product

def extract_dna_features(folder_path):

    # Iterate over files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            print("Extracting DNA features from:", filename)

            # Create a temporary file to write the modified data
            temp_file = tempfile.NamedTemporaryFile(
                            mode='w', delete=False, newline='', encoding='utf-8')
            
            # Open the CSV file for reading
            with open(file_path, 'r', newline='', encoding='utf-8') as infile, temp_file:
                reader = csv.DictReader(infile)
                
                # Define the fieldnames for the output CSV
                header = reader.fieldnames
                new_columns = []
                codons = ["".join(combination) for combination in product("ATGC", repeat=3)]
                new_columns.extend(codons)
                new_columns.extend(["cds_length", "utr5_length", 
                                   "utr3_length", "utr5_gc", "cds_gc", "utr3_gc", 
                                   "cds_wobble2_gc", "cds_wobble3_gc"])
                header.extend(new_columns)
                
                # Open the CSV file for writing
                writer = csv.DictWriter(temp_file, fieldnames=header)
                writer.writeheader()

                # Iterate over the remaining rows
                for row in reader:
                    # Add data for new columns (assuming new_columns is a list of values)
                    codon_frequencies = compute_cds_codon_frequencies(row, codons)
                    row.update(codon_frequencies)
                    
                    # Write the modified row to the temporary file
                    writer.writerow(row)
            
            # Replace the original file with the temporary file
            shutil.move(temp_file.name, file_path)

def compute_cds_codon_frequencies(row, codons):
    """Compute the frequency of every possible codon in the cds
    
    Args:
        row (dict): row extracted from the csv file. This contains the
        following fields: ensembl_gene_id, transcript_id, promoter, utr5, cds,
        utr3, terminator

        codons (list): list of strings represesenting all 64 possible codons
        e.g. AGA
    """
    
    cds = row.get("cds")
    cds_length = len(cds)
    codon_count = cds_length // 3
    # Placeholder for codon frequencies
    codon_frequencies = {codon: 0 for codon in codons}
    # Compute codon frequencies based on the sequence in the row
    for i in range(0, cds_length - 2, 3):
        codon = cds[i:i+3]
        if len(codon) == 3:
            codon_frequencies[codon] += 1
    for codon in codon_frequencies:
        codon_frequencies[codon] /= codon_count

    return codon_frequencies


# Usage example
if __name__ == "__main__":
    folder_path = "csv_files" 
    extract_dna_features(folder_path)