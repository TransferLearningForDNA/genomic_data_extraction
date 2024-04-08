import os
import csv
import tempfile
import shutil
from itertools import product


def extract_dna_features(folder_path: str) -> None:
    """ Extract and compute DNA features for each CSV file containing genomic sequences.

    Add new columns to the existing CSV files with computed codon frequencies, lengths of
    different DNA segments (utr5, cds, utr3), GC content in DNA segments, and GC content at
    wobble positions.

    Args:
        folder_path (str): The path to the folder containing genomic data CSV files.
    """
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
                if header != ["ensembl_gene_id", "transcript_id", "promoter", "utr5", "cds", "utr3", "terminator"]:
                    break
                new_columns = []
                codons = ["".join(combination) for combination in product("ACGT", repeat=3)]
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
                    utr5 = row.get("utr5")
                    cds = row.get("cds")
                    utr3 = row.get("utr3")

                    row.update(compute_cds_codon_frequencies(cds=cds, codons=codons))
                    row.update(compute_lengths(cds=cds, utr5=utr5, utr3=utr3))
                    row.update(compute_gc_content_sequence_components(utr5=utr5,
                                                                      cds=cds,
                                                                      utr3=utr3))
                    row.update(compute_gc_content_wobble_positions(cds))

                    # Write the modified row to the temporary file
                    writer.writerow(row)

            # Replace the original file with the temporary file
            shutil.move(temp_file.name, file_path)


def compute_cds_codon_frequencies(cds: str, codons: list[str]) -> dict[str, float]:
    """ Compute the frequency of every possible codon in the cds.
    
    Args:
        cds (str): cds sequence

        codons (list[str]): list of strings representing all 64 possible codons
        e.g. "AGA"

    Returns:
        dict[str, float]: dictionary of codon frequencies for all 64 possible codons,
        with codons as keys and their frequencies as values.
    """
    cds_length = len(cds)
    codon_count = cds_length // 3
    # Placeholder for codon frequencies
    codon_frequencies = {codon: 0 for codon in codons}

    # Address situation in which the cds provided is too short
    if codon_count == 0:
        return codon_frequencies

    # Compute codon frequencies based on the sequence in the row
    for i in range(0, cds_length - 2, 3):
        codon = cds[i:i + 3]
        if len(codon) == 3:
            codon_frequencies[codon] += 1

    for codon in codon_frequencies:
        codon_frequencies[codon] /= codon_count

    return codon_frequencies


def compute_lengths(cds: str, utr5: str, utr3: str) -> dict[str, int]:
    """ Compute the length of the cds, utr3 and utr5 DNA sequences.
    
    Args:
        cds (str): CDS DNA sequence.
        utr5 (str): 5' UTR DNA sequence.
        utr3 (str): 3' UTR DNA sequence.

    Returns:
        dict[str, int]: A dictionary with keys 'cds', 'utr5', and 'utr3', and integer values
                        representing the lengths of these sequences.
    """
    lengths = {"cds_length": len(cds) if len(cds) > 0 else "",
               "utr5_length": len(utr5) if len(utr5) > 0 else "",
               "utr3_length": len(utr3) if len(utr3) > 0 else ""}

    return lengths


def compute_gc_content_sequence_components(utr5: str, cds: str, utr3: str) -> dict[str, float]:
    """ Compute the GC content of the cds, utr3 and utr5.

    GC content is defined as (G + C)/(A + T + G + C), where each letter
    represents the number of times that nucleotide appears in the DNA sequence.
    
    Args:
        utr5 (str): 5' UTR DNA sequence.
        cds (str): CDS DNA sequence.
        utr3 (str): 3'UTR DNA sequence.

    Returns:
        dict[str, float]: A dictionary with keys 'cds_gc', 'utr5_gc', and 'utr3_gc',
                          and float values representing the GC content of these sequences.
    """
    utr5_gc_count = count_gc_nucleotides(utr5)
    cds_gc_count = count_gc_nucleotides(cds)
    utr3_gc_count = count_gc_nucleotides(utr3)

    utr5_length = len(utr5)
    cds_length = len(cds)
    utr3_length = len(utr3)

    utr5_gc = utr5_gc_count / utr5_length if utr5_length != 0 else ""
    cds_gc = cds_gc_count / cds_length if cds_length != 0 else ""
    utr3_gc = utr3_gc_count / utr3_length if utr3_length != 0 else ""

    gc_content = {"utr5_gc": utr5_gc,
                  "cds_gc": cds_gc,
                  "utr3_gc": utr3_gc}

    return gc_content


def count_gc_nucleotides(sequence: str) -> int:
    """ Count the number of times G and C nucleotides appear in a DNA sequence.
    
    Args:
        sequence (str): DNA sequence

    Returns:
        int: Sum of G and C counts in the sequence.
    """
    g_content = sequence.count("G")
    c_content = sequence.count("C")
    return g_content + c_content


def compute_gc_content_wobble_positions(cds: str) -> dict[str, float]:
    """ Compute the GC content of wobble positions 2 and 3 in the cds.

    GC content is defined as (G + C)/(A + T + G + C), where each letter
    represents the number of times that nucleotide appears in a given
    wobble position
    
    Args:
        cds (str): CDS DNA sequence.

    Returns:
        dict[str, float]: A dictionary with keys 'wobble2_gc' and 'wobble3_gc',
                          and float values representing the GC content at wobble positions 2 and 3
                          in the cds, respectively.
    """
    # Extract the nucleotides in positions 2 and 3 into separate lists
    wobble2_nucleotides = cds[1::3]
    wobble3_nucleotides = cds[2::3]

    wobble2_gc_count = (wobble2_nucleotides.count("G") +
                        wobble2_nucleotides.count("C"))
    wobble3_gc_count = (wobble3_nucleotides.count("G") +
                        wobble3_nucleotides.count("C"))

    # Compute the GC content
    wobble2_gc = wobble2_gc_count / len(wobble2_nucleotides) \
        if len(wobble2_nucleotides) != 0 else ""

    wobble3_gc = wobble3_gc_count / len(wobble3_nucleotides) \
        if len(wobble3_nucleotides) != 0 else ""

    gc_content = {"cds_wobble2_gc": wobble2_gc,
                  "cds_wobble3_gc": wobble3_gc}

    return gc_content


# Usage example
if __name__ == "__main__":
    folder_path = "csv_files"
    extract_dna_features(folder_path)
