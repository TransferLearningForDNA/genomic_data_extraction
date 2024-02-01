import os
import subprocess
import pandas as pd
import csv
from Bio import Entrez
from pysradb import SRAweb
from pysradb.search import SraSearch
from pysradb.sradb import SRAdb

# Configuration your NCBI API email here
Entrez.email = "your-email@example.com"


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

    for species, srx_ids in species_srx_map.items():
        print(f"\n{species}: {', '.join(srx_ids)}")

    return species_srx_map


# Step 3: Viewing the returned metadata (optional)
def view_srx_metadata(species_srx_map):
    db = SRAweb()

    all_species_metadata = {}

    for species, srx_ids in species_srx_map.items():
        list_ids = list(srx_ids)
        print(f"Processing {species} with {len(list_ids)} SRX IDs...")

        df = db.sra_metadata(list_ids)

        all_species_metadata[species] = df
        print(list(all_species_metadata[species].columns))

    return all_species_metadata


# Step 4: Storing only the needed data - SRX and SRR IDs - in a csv
def SRX_to_SRR_csv(species_srx_map, output_file):
    db = SRAweb()
    data_rows = [] 

    for species, srx_ids in species_srx_map.items():
        print(f"Processing {species} with {len(srx_ids)} SRX IDs...")

        for srx_id in srx_ids:
            df = db.sra_metadata([srx_id])
            srr_ids = df['run_accession'].unique()

            if not df.empty and 'organism_taxid' in df.columns:
                taxonomy_id = df.iloc[0]['organism_taxids']
            else:
                taxonomy_id = None  # Use None or an appropriate placeholder if taxonomy ID is not available

            # For each SRX ID, store its corresponding SRR IDs along with the taxonomy ID
            for srr_id in srr_ids:
                data_row = {
                    "species": species,
                    "taxonomy_id": taxonomy_id,
                    "srx_id": srx_id,
                    "srr_id": srr_id
                }
                data_rows.append(data_row)

    # Convert the list of dictionaries to a DataFrame
    df_output = pd.DataFrame(data_rows)

    # Save the df to a CSV file
    df_output.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# Specify our species of interest here
# NOTE: There is a discrepancy here for 'Cyanidioschyzon merolae', many entries are strain 10D - Taxonomy ID: 280699. 
# These get filtered out in this process. Not sure what we should decide to do / how to handle?

if __name__ == "__main__":
    species_data = {
    'Chlamydomonas reinhardtii': 3055,
    'Ostreococcus tauri': 70448,
    'Cyanidioschyzon merolae': 45157,
    'Homo sapiens': 9606,
    'Saccharomyces cerevisiae': 4932
    }
    
    species_srx_map = query_and_get_srx_accession_ids(species_data)
    
    # (Optional) View the returned metadata
    # all_species_metadata = view_srx_metadata(species_srx_map)
    # print(all_species_metadata['Homo sapiens'].head(5))

    SRX_to_SRR_csv(species_srx_map, 'output_srx_srr.csv')

