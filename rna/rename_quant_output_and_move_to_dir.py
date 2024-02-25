import os
import shutil

def rename_and_move_files(source_dir, destination_dir):

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
                if file == 'quant.sf':

                    # rename the file with the name of the sample directory (SRR ID)
                    new_file_name = f'quant_{subdir}.sf'
                    new_file_path = os.path.join(destination_dir, new_file_name)
                    os.rename(file_path, new_file_path)
                    
                    # move the renamed file to the destination directory
                    shutil.move(new_file_path, destination_dir)

                    print(f"Renamed '{file}' to '{new_file_name}' and moved to '{destination_dir}'")


if __name__ == "__main__":
    # source directory containing subdirectories with quant.sf files:
    # this is where the rna-seq pipeline stores the quant files for all samples from 1 species: inside the salmon directory
    source_directory = "/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/rnaseq/rnaseq_output_dir/Chlamydomonas_reinhardtii/salmon"

    # destination directory where the renamed files will be moved:
    # this is where we store all the quant files for 1 species
    destination_directory = "/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/quant_files/raw/chlamydomonas_reinhardtii/sf_files"

    # rename and move files
    rename_and_move_files(source_directory, destination_directory)
