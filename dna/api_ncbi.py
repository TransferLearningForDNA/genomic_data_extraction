import os
import subprocess


# Retrieve the API key from the environment variable
ncbi_api_key = os.getenv('NCBI_API_KEY')
if ncbi_api_key is None:
    raise EnvironmentError("NCBI API KEY not found. Please set the environment variable.")

species = "osterococcus_tauri"
taxid = "70448"

# Construct the command
command = ["./datasets", "download", "genome", "taxon", taxid, "--reference", "--include", "genome,gff3",
           "--filename", species+"_ncbi_dataset.zip", "--api-key", str(ncbi_api_key)]

# Execute the command
result = subprocess.run(command, capture_output=True, text=True)

# Check if the command was executed successfully
if result.returncode == 0:
    print("Command executed successfully.")
    print(result.stdout)
else:
    print("Error in executing command:")
    print(result.stderr)

