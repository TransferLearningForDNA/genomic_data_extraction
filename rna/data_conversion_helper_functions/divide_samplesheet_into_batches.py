import pandas as pd

# Read the CSV file into a DataFrame
species_name = "species_name"  # e.g. 'Chlamydomonas_reinhardtii'
local_path_to_full_samplesheet_for_one_species = (
    "/local/path/to/species_name_samplesheet.csv"
)
df = pd.read_csv(local_path_to_full_samplesheet_for_one_species)

# Split the DataFrame into five equal parts, each containing 10 rows
split_dfs = [df[i : i + 10] for i in range(0, len(df), 10)]

# Write each split DataFrame to a separate CSV file
for i, split_df in enumerate(split_dfs):
    local_path_to_save = "/local/path/to/save/the/csv/files"
    split_df.to_csv(
        f"{local_path_to_save}/{species_name}_split_samplesheet_{i+1}.csv", index=False
    )
