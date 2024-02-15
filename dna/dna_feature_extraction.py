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

                # Compute features for each gene
                for row in reader:
                    # Add data for new columns (assuming new_columns is a list of values)
                    row.update(compute_cds_codon_frequencies(row, codons))
                    row.update(compute_lengths(row))
                    row.update(compute_gc_content_sequence_components(row))
                    
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

    Returns:
        dict: dictionary of codon frequencies for all 64 possible codons
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


def compute_lengths(row):
    """Compute the length of the cds, utr3 and utr5
    
    Args:
        row (dict): row extracted from the csv file. This contains the
        following fields: ensembl_gene_id, transcript_id, promoter, utr5, cds,
        utr3, terminator

    Returns:
        dict: dictionary of lengths of cds, utr5 and utr3
    """
    lengths = {"cds_length" : len(row.get("cds")),
               "utr5_length" : len(row.get("utr5")),
               "utr3_length" : len(row.get("utr3"))}

    return lengths


def compute_gc_content_sequence_components(row):
    """Compute the gc content of the cds, utr3 and utr5
    
    Args:
        row (dict): row extracted from the csv file. This contains the
        following fields: ensembl_gene_id, transcript_id, promoter, utr5, cds,
        utr3, terminator

    Returns:
        dict: dictionary of gc content of cds, utr5 and utr3
    """
    utr5 = row.get("utr5")
    cds = row.get("cds")
    utr3 = row.get("utr3")

    utr5_gc = count_gc_nucleotides(utr5)
    cds_gc = count_gc_nucleotides(cds)
    utr3_gc = count_gc_nucleotides(utr3)

    utr5_length = len(utr5)
    cds_length = len(cds)
    utr3_length = len(utr3)

    gc_content = {"utr5_gc":utr5_gc/utr5_length,
                  "cds_gc":cds_gc/cds_length,
                  "utr3_gc":utr3_gc/utr3_length}

    return gc_content


def count_gc_nucleotides(sequence):
    """Count the number of times G and C nucleotides appear in a DNA sequence
    
    Args:
        sequence (str): DNA sequence

    Returns:
        int: count of G nucleotides in the sequence
        int: count of C nucleotides in the sequence
    """
    g_content = sequence.count("G")
    c_content = sequence.count("C")
    return g_content + c_content


# Usage example
if __name__ == "__main__":
    folder_path = "csv_files" 
    extract_dna_features(folder_path)