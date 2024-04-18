from typing import Dict, List
import pandas as pd

from pysradb import SRAweb
from pysradb.search import SraSearch


def query_sra(species: str, taxonomy_id: int) -> pd.DataFrame | None:
    """Query the SRA database for RNA-seq species metadata results given a species name and taxonomy ID.

    Args:
        species (str): Species scientific name (format e.g. 'Homo sapiens')
        taxonomy_id (int): Taxonomy ID of the species (e.g. 9606)

    Returns:
        DataFrame: Species metadata RNA-seq results (contains experiment accession IDs)
    """
    # First, search for 'RNA-Seq' strategy
    try:
        sra_search_rna_seq = SraSearch(
            organism=species, layout="paired", strategy=["RNA-Seq"], return_max=50
        )
        sra_search_rna_seq.search()
        df_rna_seq = sra_search_rna_seq.get_df()

        # If 'RNA-Seq' results are fewer than 50, search with 'OTHER' strategy
        df_other = pd.DataFrame()
        if len(df_rna_seq) < 50:
            additional_results_needed = 50 - len(df_rna_seq)
            sra_search_other = SraSearch(
                organism=species,
                layout="paired",
                strategy=["OTHER"],
                return_max=additional_results_needed,
            )
            sra_search_other.search()
            df_other = sra_search_other.get_df()

        # Combine the two DataFrames
        df_combined = pd.concat([df_rna_seq, df_other], ignore_index=True)
        # print(f"{species} df_combined:", df_combined.columns)

        # Filter these combined dataframes to ensure they match the taxonomy ID
        df_filtered = df_combined[df_combined["sample_taxon_id"] == str(taxonomy_id)]

        return df_filtered if not df_filtered.empty else None

    except (ValueError, KeyError, AttributeError) as e:
        print(f"Error querying {species}: {e}")
        return None
    except Exception as e:
        print(
            f"Error querying {species}, possibly due to external libraries or API (SraSearch): {e}"
        )
        return None


def query_and_get_srx_accession_ids(
    species_data: Dict[str, int]
) -> Dict[str, List[str]]:
    """Get experiment accession numbers (SRX IDs) for each species.

    Args:
        species_data (Dict[str, int]): A dictionary with species names as keys and taxonomy IDs as values.

    Returns:
        Dict[str, List[str]: A dictionary with species names as keys and SRX (experiment accession) ID as values.
    """
    # Dictionary to store species names and their SRX IDs
    species_srx_map = {}

    for species, tax_id in species_data.items():
        df = query_sra(species, tax_id)

        if df is not None and not df.empty:
            srx_ids = df["experiment_accession"].unique()
            species_srx_map[species] = srx_ids
        else:
            print(f"No results or empty DataFrame for {species}")

    for species, srx_ids in species_srx_map.items():
        print(f"\n{species}: {', '.join(srx_ids)}")

    return species_srx_map


def view_srx_metadata(species_srx_map: Dict[str, List[str]]) -> Dict[str, pd.DataFrame]:
    """Get metadata for all species and experiment accession numbers.

    Args:
        species_srx_map (Dict[str, List[str]]): A dictionary with species names as keys and SRX (experiment accession) IDs as values.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary with species name as keys and dataframes with experiment metadata as values.
    """
    db = SRAweb()

    all_species_metadata = {}

    for species, srx_ids in species_srx_map.items():
        list_ids = list(srx_ids)
        print(f"Processing {species} with {len(list_ids)} SRX IDs...")

        df = db.sra_metadata(list_ids)

        all_species_metadata[species] = df
    print(list(all_species_metadata[0].columns))

    return all_species_metadata


def SRX_to_SRR_csv(species_srx_map: Dict[str, List[str]], output_file: str) -> None:
    """Save a CSV file with columns for species, taxonomy_id, srx_id, and corresponding srr_ids.

    This function processes each species and its SRX IDs to fetch SRR IDs and taxonomy IDs from the SRA database,
    and then compiles this information into a CSV file.
    This file can be used for downloading data and for logic handling in later stages of processing and testing.

    Args:
        species_srx_map (Dict[str, List[str]]): A dictionary with species names as keys and lists of SRX (experiment accession) IDs as values.
        output_file (str): The path to the output CSV file where the data will be saved.
    """
    db = SRAweb()
    data_rows = []

    for species, srx_ids in species_srx_map.items():
        print(f"Processing {species} with {len(srx_ids)} SRX IDs...")

        for srx_id in srx_ids:
            df = db.sra_metadata([srx_id])
            srr_ids = df["run_accession"].unique()

            if not df.empty and "organism_taxid" in df.columns:
                taxonomy_id = df.iloc[0]["organism_taxid"]
            else:
                taxonomy_id = None  # Use None or an appropriate placeholder if taxonomy ID is not available

            # For each SRX ID, store its corresponding SRR IDs along with the taxonomy ID
            for srr_id in srr_ids:
                data_row = {
                    "species": species,
                    "taxonomy_id": taxonomy_id,
                    "srx_id": srx_id,
                    "srr_id": srr_id,
                }
                data_rows.append(data_row)

    # Convert the list of dictionaries to a DataFrame
    df_output = pd.DataFrame(data_rows)

    # Save the df to a CSV file
    df_output.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")


# Specify our species of interest here
if __name__ == "__main__":
    species_tax_id = {
        "Chlamydomonas reinhardtii": 3055,
        "Galdieria sulphuraria": 130081,
        "Cyanidioschyzon merolae": 45157,
        "Homo sapiens": 9606,
        "Saccharomyces cerevisiae": 4932,
    }

    species_srx_ids = query_and_get_srx_accession_ids(species_tax_id)

    # (Optional) View the returned metadata
    # all_species_metadata = view_srx_metadata(species_srx_map)
    # print(all_species_metadata['Homo sapiens'].head(5))

    SRX_to_SRR_csv(species_srx_ids, "output_srx_srr.csv")
