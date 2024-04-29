import subprocess
import os
import datetime
from typing import Optional
import pandas as pd
from pysradb import SRAweb


def download_sra_data(
    csv_file_path: str, output_directory: str, limit: Optional[int] = 10
) -> None:
    """Download SRA data based on SRR IDs listed in a CSV file using the fasterq-dump command from the SRA toolkit.

    Be aware of two critical requirements:
    1. SRA-toolkit installation: Ensure the correct version is installed in your environment as fasterq-dump may raise errors.
    2. Download limit parameter: This limit is set to 10 by default due to the large size of files (typically >15GB per run) which can heavily impact memory and disk usage.

    Args:
        csv_file_path (str): The file path to the CSV containing SRR IDs for download.
        output_directory (str): The directory where downloaded files will be saved.
        limit (Optional[int]): Maximum number of files to download. Defaults to 10 to avoid excessive bandwidth and storage usage.

    Returns:
        None: This function does not return a value but outputs files to the specified directory.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    SRAweb()
    download_count = 0

    for _, row in df.iterrows():
        if download_count >= limit:
            print(f"Reached download limit of {limit}.")
            break

        srr_id = row["srr_id"]
        species_name = row["species"]

        # check that the fasta files have not already been downloaded
        # for this sample (i.e. SRR ID)
        output_file = os.path.join(output_directory, f"{srr_id}_1.fastq")
        compressed_output_file = os.path.join(output_directory, f"{srr_id}_1.fastq.gz")

        if (
            row["species"] == species_name
            and (not os.path.exists(output_file))
            and (not os.path.exists(compressed_output_file))
        ):
            try:
                print(
                    f"Starting download of SRR ID {srr_id} at {datetime.datetime.now()}",
                    flush=True,
                )
                # Download using the fasterq-dump command for each SRR ID (construct as a list)
                command = ["fasterq-dump", srr_id, "--outdir", output_directory]
                subprocess.run(command, check=True)

                print(
                    f"SRR ID {srr_id} downloaded to {output_directory} at {datetime.datetime.now()}",
                    flush=True,
                )

                download_count += 1

                # list files in the output directory after each download
                print(f"Files in {output_directory} after download:")
                print(os.listdir(output_directory))

            except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
                print(f"An error occurred while processing {srr_id}: {e}", flush=True)
            except Exception as e:
                print(f"An unexpected error occurred: {e}", flush=True)


if __name__ == "__main__":  # pragma: no cover, main function to download SRA data
    # Call CSV file path returned by the 'query_and_csv_production' file
    path_to_csv = "/local/path/to/output_srx_srr.csv"

    # Output dir here
    path_to_output_folder = "/local/path/to/save/fastaq/files/"

    download_sra_data(path_to_csv, path_to_output_folder)
