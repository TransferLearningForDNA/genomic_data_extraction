import ensembl_rest
import requests
import csv
import re
import sys
import os
import time
from typing import Optional



def read_gene_ids_from_file(file_path: str) -> list[str]:

    """ Reads gene IDs from a file, skipping the first line.

    Args:
        file_path (str): The path to the file containing gene IDs.

    Returns:
        list: A list of gene IDs read from the file.
    """
    try:
        with open(file_path, 'r') as file:
            # Skip the first line
            next(file)

            # Read gene IDs from the remaining lines
            gene_ids = [line.strip() for line in file]

        return gene_ids
    except FileNotFoundError:
        # Handle file not found error
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        # Handle other exceptions
        print(f"Error: {str(e)}")
        return []


def get_cds(transcript_id: str) -> str:
    """
    Retrieves the coding sequence (CDS) for a given Ensembl transcript ID.

    Args:
        transcript_id (str): Ensembl transcript ID for the target gene.

    Returns:
        str: The nucleotide sequence of the coding sequence (CDS).
             Returns an empty string in case of an error.
    """
    # Construct the REST API URL for retrieving CDS
    address = f"https://rest.ensembl.org/sequence/id/{transcript_id}?multiple_sequences=1;type=cds"

    try:
        # Make a GET request to the Ensembl REST API
        r = requests.get(address, headers={"Content-Type": "text/x-fasta"})

        # Ensure that there are no issues with the sequence request
        r.raise_for_status()

        # Extract only the nucleotide sequence and format into a single string
        raw_output = r.text
        pattern = re.compile('(?:^|\n)[ATGC]+')
        matches = pattern.findall(raw_output)
        cds_sequence = ''.join(matches).replace('\n', '')

        return cds_sequence

    except requests.exceptions.RequestException as e:
        # If there's an error with the request, print the error and return an empty string
        print(f"Error with the request for {transcript_id}: {e}")
        return ''

    
    
def get_promoter_terminator(transcript_id: str, promoter_length=1000 , terminator_length=500) -> tuple[str, str]:
    """
    Retrieves the promoter and terminator sequences for a given Ensembl transcript ID.

    Args:
        transcript_id (str): Ensembl transcript ID for the target gene.
        promoter_length (int, optional): Length of the promoter sequence (default is 1000).
        terminator_length (int, optional): Length of the terminator sequence (default is 500).

    Returns:
        tuple: A tuple containing the promoter and terminator sequences as strings.
    """
    # Construct the REST API URL for retrieving genomic sequence with specified 5' and 3' expansions
    address = f"https://rest.ensembl.org/sequence/id/{transcript_id}?type=genomic;expand_5prime=1000;expand_3prime=500"

    try:
        # Make a GET request to the Ensembl REST API
        r = requests.get(address, headers={"Content-Type": "text/x-fasta"})

        # Ensure that there are no issues with the sequence request
        r.raise_for_status()
        
        # Remove unwanted characters to produce only the nucleotide sequence and format into a single string
        raw_output = r.text
        pattern = re.compile('(?:^|\n)[ATGC]+')
        matches = pattern.findall(raw_output)
        sequence = ''.join(matches).replace('\n', '')

        # Extract the promoter and terminator sequence from the entire sequence
        promoter_sequence = sequence[:promoter_length]
        terminator_sequence = sequence[-terminator_length:]
        
        return promoter_sequence, terminator_sequence

    except requests.exceptions.RequestException as e:
        # If there's an error with the request, print the error and return an empty string
        print(f"Error with the promoter-terminator request for {transcript_id}: {e}")
        return '', ''

def extract_utr_information(data: dict) -> tuple[list[tuple[int, int]], list[tuple[int, int]], Optional[str], Optional[int]]:
    """ Extracts information about 5' and 3' UTRs (Untranslated Regions) from the provided data.

    Args:
        data (dict): A dictionary containing information about UTRs.

    Returns:
        tuple: A tuple containing lists of 5' UTRs, 3' UTRs, chromosome, and strand information.
    """
    # Retrieve UTR data from the input dictionary
    utr_data = data.get('UTR', [])

    # Initialize lists to store 5' UTR and 3' UTR information
    utr5_list = []
    utr3_list = []

    # Iterate through UTR entries in the data
    for utr_entry in utr_data:
        utr_type = utr_entry.get('type', '')
        utr_start = utr_entry.get('start', None)
        utr_end = utr_entry.get('end', None)

        # Check if the UTR entry has valid type, start, and end information
        if utr_type and utr_start is not None and utr_end is not None:
            # Categorize UTRs into 5' and 3' UTR lists
            if utr_type == 'five_prime_utr':
                utr5_list.append((utr_start, utr_end))
            elif utr_type == 'three_prime_utr':
                utr3_list.append((utr_start, utr_end))

    # Extract chromosome and strand information
    chromosome = utr_entry['seq_region_name'] if utr_data else None
    strand = data.get('strand', None)

    return utr5_list, utr3_list, chromosome, strand


def get_utr_sequence(chromosome: str, strand: int, start: int, end: int, species: str) -> str:
    """ Retrieves the nucleotide sequence of a UTR (Untranslated Region) from the Ensembl database.

    Args:
        chromosome (str): Chromosome name or identifier.
        strand (int): Strand information (1 for forward strand, -1 for reverse strand).
        start (int): Start position of the UTR on the chromosome.
        end (int): End position of the UTR on the chromosome.
        species (str): Species for which the UTR sequence is requested.

    Returns:
        str: The nucleotide sequence of the specified UTR.
    """
    # Use Ensembl REST API to retrieve UTR sequence for the specified region
    region = f"{chromosome}:{start}..{end}:{strand}"
    try:
        utr_sequence = ensembl_rest.sequence_region(region=region, species=species)["seq"]
    except ensembl_rest.core.restclient.HTTPError as e:
        if e.response.status_code == 429:  # Check for rate limit exceeded error
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(1)
            utr_sequence = get_utr_sequence(chromosome, strand, start, end, species)
            
    return utr_sequence


def get_full_utr_sequence(list_utr_coordinates: list[tuple[int, int]], chromosome: str, strand: int, species: str) -> str:
    """ Retrieves the concatenated nucleotide sequence of multiple UTRs from the Ensembl database.

    Args:
        list_utr_coordinates (list): A list of tuples representing UTR start and end coordinates.
        chromosome (str): Chromosome name or identifier.
        strand (int): Strand information (1 for forward strand, -1 for reverse strand).

    Returns:
        str: The concatenated nucleotide sequence of the specified UTRs.
    """
    # Initialize an empty string to store the concatenated UTR sequence
    concatenated_sequence = ""

    # Iterate through UTR coordinates and retrieve individual UTR sequences
    for start, end in list_utr_coordinates:
        sequence = get_utr_sequence(chromosome, strand, start, end, species)
        concatenated_sequence += sequence

    return concatenated_sequence


def get_species_name(file_path: str) -> str:
    """ Extracts the species name from a file path.

    Args:
        file_path (str): The path to the file containing the species information.

    Returns:
        str: The extracted species name.
    """
    # Extract the filename from the path
    filename = os.path.basename(file_path)

    # Remove the extension
    filename_without_extension = filename.rsplit('.', 1)[0]

    # Split the filename by underscore and get the last two parts
    species = "_".join(filename_without_extension.split("_")[:2])

    return species

def request_with_retry(transcript_id: str) -> dict:
    """ Retries the request for a transcript ID
    
    Args:
        transcript_id (str): Ensembl transcript ID for the target gene.

    Returns:
        dict: A dictionary containing information about the transcript.
    
    """
    while True:
        try:
            transcript_data = ensembl_rest.lookup(id=transcript_id, params={'expand': True, 'utr': True})
            return transcript_data
        except ensembl_rest.core.restclient.HTTPError as e:
            if e.response.status_code == 429:  # Check for rate limit exceeded error
                print("Rate limit exceeded. Waiting before retrying...")
                time.sleep(1)
                continue
            else:
                print(f"Error with the request for {transcript_id}: {e}")
                return {}
   
def get_data_as_csv(file_paths: list[str], output_directory: str):
    """ Retrieves data for gene IDs from Ensembl, processes it, and saves it as CSV files.

    Args:
        file_paths (list): List of file paths containing gene IDs.
        output_directory (str): Directory where CSV files will be saved.

    Returns:
        None
    """
    # Create the directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    for file_path in file_paths:
        # Read gene IDs from the file
        gene_ids = read_gene_ids_from_file(file_path)

        # Generate output filename and species name
        filename = "ensembl_data_" + get_species_name(file_path) + ".csv"
        species = " ".join(get_species_name(file_path).split("_"))

        print(f"Starting data extraction for {species}.")

        # Initialize a CSV writer
        filename = os.path.join(output_directory, filename)
        csv_file = open(filename, "w", newline="")
        csv_writer = csv.writer(csv_file)

        # Write the header to the CSV file
        csv_writer.writerow(["ensembl_gene_id", "transcript_id", "promoter", "utr5", "cds", "utr3", "terminator"])

        # Loop through each gene ID and retrieve the data
        for gene_id in gene_ids:
            time.sleep(2)
            print(f"Extracting data for gene ID : {gene_id}")
            
            try:
                gene_data = ensembl_rest.lookup(species=species, id=gene_id)

            except ensembl_rest.core.restclient.HTTPError as e:
                if e.response.status_code == 429:  # Check for rate limit exceeded error
                    print("Rate limit exceeded. Waiting before retrying...")
                    time.sleep(1)
                    gene_data = ensembl_rest.lookup(species=species, id=gene_id)

            # Get transcript ID
            transcript_id = gene_data["canonical_transcript"].split(".")[0]

            # Retrieve promoter, CDS, and terminator sequences
            cds_sequence = get_cds(transcript_id)
            if cds_sequence == '':
                continue
            promoter_sequence, terminator_sequence = get_promoter_terminator(transcript_id)

            # Retrieve UTR sequences
            transcript_data = request_with_retry(transcript_id)
            if transcript_data == {}:
                continue

            utr5_coord_list, utr3_coord_list, chromosome, strand = extract_utr_information(transcript_data)
            utr5_sequence = get_full_utr_sequence(utr5_coord_list, chromosome, strand,
                                                  species=get_species_name(file_path))
            utr3_sequence = get_full_utr_sequence(utr3_coord_list, chromosome, strand,
                                                  species=get_species_name(file_path))

            # Write the row to the CSV file
            csv_writer.writerow([gene_id, transcript_id, promoter_sequence, utr5_sequence, cds_sequence, utr3_sequence,
                                 terminator_sequence])

        # Close the CSV file
        csv_file.close()

        print(f"Data extraction for {species} is now complete.")


if __name__ == "__main__":
    
    folder = "gene_lists/"
    # Specify the list of file paths for gene lists
    file_paths = ["homo_sapiens_genes.txt", "saccharomyces_cerevisiae_genes.txt", "chlamydomonas_reinhardtii_genes.txt", "galdieria_sulphuraria_genes.txt", "cyanidioschyzon_merolae_genes.txt"]

    # Prepend the folder path to each file path
    file_paths = [folder + path for path in file_paths]
    
    get_data_as_csv(file_paths, "csv_files")