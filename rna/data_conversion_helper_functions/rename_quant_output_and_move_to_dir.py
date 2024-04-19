import os


def rename_and_move_files(source_dir: str, destination_dir: str):
    """Rename 'quant.sf' files in each subdirectory of the source directory with a new name
    based on the subdirectory name (SRR ID), then move them to a specified
    destination directory.

    Args:
        source_dir (str): The directory containing subdirectories for each sample. Each
                          subdirectory is named with an SRR ID and contains a 'quant.sf' file.
        destination_dir (str): The target directory where renamed files will be moved (species-specific).

    Returns:
        None: Files are renamed and moved without returning any value.
    """

    # iterate through subdirectories in the source directory
    for subdir in os.listdir(source_dir):

        subdir_path = os.path.join(source_dir, subdir)

        # check if subdir is a directory:
        # this should be a directory for a specific sample (with the name being an SRR ID)
        if os.path.isdir(subdir_path):

            # iterate through files in the subdirectory
            for file in os.listdir(subdir_path):

                file_path = os.path.join(subdir_path, file)

                # retrieve the quant.sf file of this sample
                if file == "quant.sf":
                    # rename the file with the name of the sample directory (SRR ID) AND move
                    new_file_name = f"quant_{subdir}.sf"
                    new_file_path = os.path.join(destination_dir, new_file_name)
                    os.rename(file_path, new_file_path)

                    print(
                        f"Renamed '{file}' to '{new_file_name}' and moved to '{destination_dir}'"
                    )


if __name__ == "__main__":
    # Source directory containing subdirectories with quant.sf files:
    # this is where the rna-seq pipeline stores the quant files for all samples from 1 species: inside the salmon directory
    source_directory = "/local/path/to/quant/sf/files/for/one/species"

    # Destination directory where the renamed files will be moved:
    # this is where we store all the quant files for 1 species
    destination_directory = (
        "/local/path/to/save/the/renamed/quant/sf/files/for/one/species"
    )

    # rename and move files
    rename_and_move_files(source_directory, destination_directory)
