# -*- coding: utf-8 -*-
"""mRNA_downloads_pysrad.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IuhQg7bZFlNn2Yihhi5zF_fgOMmxSCb8

# Using Pysradb
Install & import statements (for required libraries):

Severl libraries were investigated and attempted for use, e.g. SQL querying on Wthena, but ultimately I have chosen to go ahead with Pysradb as it seems to offer the most aligned funtionality with our goals.
"""

!pip install git+https://github.com/saketkc/pysradb
!pip install joblib pandas biopython

from pysradb import SRAweb
from pysradb.search import SraSearch
import pandas as pd
from Bio import Entrez

"""# Getting data
## 1. Context: Understanding the underlying SRA Database querying structure
NOTE (Important & confusing): NCBI follows this hiererachy: SRP => SRX => SRR.


---
*   Each SRP (**project**) has multiple SRX (**experiments**) and each SRX in turn has multiple SRR **(runs**) inside it.


*   We need to mimick this hiereachy to access our downloads.


*   The reason to do that is simple: in most cases you care about SRX (experiment) the most, and would want to “merge” your SRRs in one way or the other.


*   Having this hierearchy ensures that downstream code can handle such cases easily, without worrying about which runs (SRR) need to be merged.
[link text](https://)

*   Using the experiment accession ids (SRX), we can fetch species metadata. Then we are able to download everything at once.



---


To get an API key:
"Users can obtain an API key now from the Settings page of their NCBI account (to create an account, visit http://www.ncbi.nlm.nih.gov/account/)."

## 2. Returning search results for each species

### Step 1: Query NCBI SRA Database
*   In 'step 1', we are using SraSearch to search through by the latin species name (organism = species).
    *   This is simply because there is NO OPTION to query by taxonomy id. I have had to implement this functionality after, manually, as you see.
    *   This will return the overall metadata for each species
---

*   First, we will try to search the database by using the 'RNA-Seq' strategy, layout="paired" and returning a maximum of 50 results.


*   If the'RNA-Seq' search returns fewer than 50 results, we will then search with 'OTHER' strategy. This is because I found on the web that some of the species in focus have their RNA data stored under this strategy type.
---
*  After this I will combine the two DataFrames returned above, and enclude only entries where the taxonomy id column **exactly** matches our Taxonomy id entered.
  *  This is our 'df_filtered' output

---

### Step 2: Return experiment accession numbers from our Species Dictionary using the above 'query_sra' function
*  Here, a new dictionary 'species_srx_map' is created to store a list of returned experiment accession ids (srx_ids) for each species.
"""

# Put your personal NCBI API email here
Entrez.email = "megan.howard19@imperial.ac.uk"

# Step 0: Specify our species of interest here

# Dictionary of species scientific names and their corresponding taxonomy IDs. NOTE: There is a discrepancy here for 'Cyanidioschyzon merolae',
# many entries are strain 10D - Taxonomy ID: 280699. These get filtered out in this process. Not sure what we should decide to do / how to handle.
species_data = {
    'Chlamydomonas reinhardtii': 3055,
    'Ostreococcus tauri': 70448,
    'Cyanidioschyzon merolae': 45157,
    'Homo sapiens': 9606,
    'Saccharomyces cerevisiae': 4932
}

# Step 1: Query NCBI SRA Database -> outputs species metadata
def query_sra(species, taxonomy_id):
    # First, search with 'RNA-Seq' strategy
    try:
        sra_search_rna_seq = SraSearch(organism=species, layout="paired", strategy=['RNA-Seq'], return_max=50)
        sra_search_rna_seq.search()
        df_rna_seq = sra_search_rna_seq.get_df()

        # If 'RNA-Seq' results are fewer than 50, search with 'OTHER' strategy
        df_other = pd.DataFrame()
        if len(df_rna_seq) < 50:
            additional_results_needed = 50 - len(df_rna_seq)
            sra_search_other = SraSearch(organism=species, layout="paired", strategy=['OTHER'], return_max=additional_results_needed)
            sra_search_other.search()
            df_other = sra_search_other.get_df()

        # Combine the two DataFrames
        df_combined = pd.concat([df_rna_seq, df_other], ignore_index=True)
        # print(f"{species} df_combined:", df_combined.columns)

        # Filter these combined dataframes to ensure they match the taxonomy ID
        df_filtered = df_combined[df_combined['sample_taxon_id'] == str(taxonomy_id)]

        return df_filtered if not df_filtered.empty else None

    except Exception as e:
        print(f"Error querying {species}: {e}")
        return None

# Step 2: Function to query by Species Dictionary, and return experiment accession numbers
def query_and_get_srx_accession_ids(species_data):
    # Dictionary to store species names and their SRX IDs
    species_srx_map = {}

    for species, tax_id in species_data.items():
        df = query_sra(species, tax_id)

        if df is not None and not df.empty:
            srx_ids = df['experiment_accession'].unique()
            species_srx_map[species] = srx_ids
        else:
            print(f"No results or empty DataFrame for {species}")

    return species_srx_map

species_srx_map = query_and_get_srx_accession_ids(species_data)

for species, srx_ids in species_srx_map.items():
    print(f"\n{species}: {', '.join(srx_ids)}")

"""## Viewing the metadata (optional)"""

db = SRAweb()
# Step 3: Viewing the data
def view_srx_metadata(species_srx_map):
    all_species_metadata = {}

    for species, srx_ids in species_srx_map.items():
        list_ids = list(srx_ids)
        print(f"Processing {species} with {len(list_ids)} SRX IDs...")

        df = db.sra_metadata(list_ids)

        all_species_metadata[species] = df

    return all_species_metadata

# Call the function and store
all_species_metadata = view_srx_metadata(species_srx_map)

print(all_species_metadata['Homo sapiens'].head(5))

"""Tests if the fasterq is working (I had many issues). You will need the sra-toolkit downloaded for this because fasterq-dump is part of the SRA Toolkit, not installed by default in Google Colab."""

!apt-get install sra-toolkit
!fasterq-dump DRR522926 --outdir '/content/drive/My Drive/SRA_downloads'

"""# Automating downoads:

You will need to authorise your drive access before running this cell or else you'll encounter credential permission errors.

I have limited the below to 5 downloads per species - Someone mentioned we are looking to work with 50 per species - but I have limited due to the time downloads take.

**NOTE** We also need to check here if the amount of runs that are returned by each srx_ids could ever end up being more than 1 run per experiment.

Currently we are only getting 1 per experiment (see/uncomment print at the end of step 2 - output downloads per SRR accesion id - section).


"""

# Step 4: Download the Data
import subprocess
import os
from google.colab import drive
drive.mount('/content/drive')

# Was having download location issues (have modified to raw string
# format even though it shouldn't really be an issue...)
output_directory = r'/content/drive/My Drive/SRA_downloads'


# species_srx_map = dict
db = SRAweb()

def download_sra_data(species_srx_map, limit=5):
    for species, srx_ids in species_srx_map.items():
        print(f"Downloading data for {species}...")
        download_count = 0

        for srx_id in srx_ids:
            if download_count >= limit:
                break  # Stop after 5 downloads

            try:
                # Fetch metadata for the SRX ID
                df = db.sra_metadata([srx_id])

                # Extract SRR IDs from the metadata
                srr_ids = df['run_accession'].unique()

                for srr_id in srr_ids:
                    # Download using the fasterq-dump command for each SRR ID
                    !fasterq-dump {srr_id} --outdir '/content/drive/My\ Drive/SRA_downloads'

                    # Uncomment the below if you want these to actually download
                    command = ['fasterq-dump', srr_id, '--outdir', output_directory, '--gzip']
                    subprocess.run(command, check=True)
                    print(f"For srx_id: {srx_id}, srr_id: {srr_id} downloaded!")

                    # Or OS approach - construct the command as a single string & execute
                    # command = f"fasterq-dump {srr_id} --outdir '{output_directory}' --gzip"
                    # os.system(command)

                    download_count += 1
                    if download_count >= limit:
                        break

            except Exception as e:
                print(f"Error downloading data for {species}, SRX ID {srx_id}: {e}")

download_sra_data(species_srx_map)

#Unused Function: Retrieve SRX Accession IDs
# def get_srx_accession_ids(df):
#     if df is not None and not df.empty:
#         try:
#             return df['experiment_accession'].unique(), df
#         except KeyError:
#             print(f"'experiment_accession' not found in DataFrame for {species}")
#             return [], df
#     else:
#         print(f"No data found for {species}")
#         return [], df