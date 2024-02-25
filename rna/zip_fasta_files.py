import os
import gzip

def zip_files(directory):
    
    # list all files in the specified directory
    files = os.listdir(directory)
    
    for file in files:
        
        # check if file is not already zipped
        if not file.endswith('.gz'):

            # full file path
            file_path = os.path.join(directory, file)
            
            # full zipped file path
            gzipped_file_path = file_path + '.gz'
            
            # check if this is a file
            if os.path.isfile(file_path):

                # open original file for reading
                with open(file_path, 'rb') as f_in:

                    # open gzipped file for writing
                    with gzip.open(gzipped_file_path, 'wb') as f_out:
                        
                        # compress the original file
                        f_out.writelines(f_in)
                
                # delete the original fasta file
                os.remove(file_path)
                
                print(f"File '{file}' zipped successfully.")

            else:
                print(f"Skipping '{file}': it's not a regular file.")
        else:
            print(f"Skipping '{file}': it's already gzipped.")

#  local directory containing the fasta files for 1 species
directory = '/Users/dilay/Documents/Imperial/genomic_data_extraction/rna/rnaseq/input_dir/Chlamydomonas_reinhardtii/fasta'

# zip the fasta files
zip_files(directory)
