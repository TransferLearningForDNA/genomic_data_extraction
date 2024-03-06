# Expression Prediction Data Preprocessing Pipeline

## Overview
This repository contains a pipeline for collecting, processing, and storing DNA and mRNA expression
profile data of given species from publicly available genetic databases.

## Features

### 1. Data Acquisition:

- Extract DNA data from Ensembl genomic database. Includes nucleotide sequences of gene components
  (promoter, 5'UTR, CDS, 3'UTR and terminator) for each protein-coding gene.
- Extract mRNA data from NCBI SRA. Gene expression data is obtained using nf-core/rnaseq processing workflow.

### 2. Data Preprocessing:

- Calculate required codon frequency, GC content, and sequence length features for genomic data.
- Calculate Relative Standard Deviation (RSD) and median expression, and filter genes with RSD < 2.
- Merge genomic and transcriptomic data tables by gene ID.

### 3. Data Preparation for Machine Learning:

- Discount irrelevant genes (low expression).
- Pad remaining promoters and terminators to standardise length.
- Pad all UTRs to the same length to ensure consistency.
- Drop genes with incomplete regulatory sequences.
- Combine all sequences (with equal length) into a unified dataset.
- One-Hot Encode (OHE) and stack sequence data for machine learning model compatibility.

## Table of Contents

## Prerequisites
List of software, libraries, and tools required (e.g., Python, AWS CLI, etc.).

## Installation
Step-by-step guide on setting up the environment and installing dependencies.

### NCBI SRA Toolkit (for the rnaseq workflow)

The fasterq-dump command-line tool, part of the NCBI SRA Toolkit, also needs to be installed on your system or available in your system's PATH. brew install sra-toolkit. Note I did this in a local venv (recommend using a venv) using the followign steps:

Download the SRA Toolkit:
1. `run on terminal: curl --output sratoolkit.tar.gz https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-mac64.tar.gz`

2. `tar -vxzf sratoolkit.current-mac64.tar.gz`
3. `export PATH=$PATH:$PWD/the_name_of_your_extracted_directory/bin`
e.g. mine was : `"sratoolkit.3.0.10-mac-x86_64"`

4. Then to avoid having to set the PATH every time, you can add the export line to your shell's profile script (example path given below, change it to your path):
`echo 'export PATH=$PATH:/Users/meghoward/Documents/Imperial MSc/Term_2/Phycoworks/genomic_data_extraction/rna/sratoolkit.3.0.10-mac-x86_64/bin' >> ~/.zshrc`

5. Activate venv whenever I want to run the code: my venv - `source notebook_to_py/bin/activate`

### Dependencies (for the rnaseq workflow)

1. First, create a conda virtual environment: `conda create --name <name_of_your_env>`. This environment will be stored inside, e.g., one of the directories for the miniconda distribution where your `conda` is from. We recommend using conda because most packages that the RNA sequencing worklow from nextflow uses can be easily installed using the bioconda channel of conda.

2. Activate your new environment: `conda activate`

3. Install the following packages, after ensuring your virtual environment is activated:

   - `conda install trim-galore`: you may need to `conda upgrade trim-galore` to get rid of an issue that has do with an obsolete `—cores` flag that is no longer used in newer versions of trim-galore
   - `conda install gffread`
   - `conda install fq`
   - `conda install -c conda-forge -c bioconda salmon=1.3.0`: specify the version for salmon, otherwise `conda install salmon` installs an obsolete version that does not integrate well with the other dependencies


## Usage
Instructions on how to use the pipeline (starting from the *outputs* of the RNA sequencing workflow), including commands and expected inputs/outputs.

TBC

## Directory Structure
Description of the repository's organization, explaining what each file and folder contains.

### dna/

#### gene_lists/

#### test/
    - csv_files/
    - gene_lists/
    - ground_truth_components/
    - test_dna_extracted.py

#### dna_extraction.py
#### dna_feature_extraction.py
#### ensembl_api.py
#### removeshortpromotersandterminators.py



### rna/

#### rna_download_logic/

This repository contains Python scripts for extracting RNA data from the NCBI Sequence Read Archive (SRA) database. It includes functionalities for querying metadata from the SRA database, retrieving experiment accession numbers, and downloading SRA data.

##### query_and_csv_production.py

    This script queries the NCBI SRA database for a given species and taxonomy ID. It retrieves metadata for RNA-Seq experiments and stores the results in a DataFrame.
        
    Functions:

        query_sra(species, taxonomy_id): Queries the SRA database for metadata of RNA-Seq experiments for a given species and taxonomy ID.

        query_and_get_srx_accession_ids(species_data): Calls query_sra() for each species in a dictionary and creates a dictionary mapping species names to their experiment accession numbers (SRX IDs).

        view_srx_metadata(species_srx_map): Populates a dictionary with DataFrames containing metadata for each species (optional).

        SRX_to_SRR_csv(species_srx_map, output_file): Saves the species names, taxonomy IDs, SRX IDs, and corresponding SRR IDs to a CSV file.

            You must manually enter your Entrez.email and species data input.


    Usage:

        Querying SRA Database:

            Edit species_data dictionary in query_sra.py to specify the species of interest along with their taxonomy IDs.

            Run query_sra.py to query the SRA database and generate a CSV file (output_srx_srr.csv) containing the metadata.

##### mRNA_fastq_download.py

    This script downloads SRA data using the fasterq-dump command for each SRR ID listed in the CSV file generated by query_and_get_srx_accession_ids().
        
    Functions:

        download_sra_data(csv_file_path, output_directory, limit=1): Downloads SRA data using fasterq-dump command from the CSV file containing SRR IDs.


    Usage:

        Downloading SRA Data:

            Ensure SRA-toolkit is installed correctly in your environment.

            Specify the CSV file path (csv_file_path) and output directory (output_directory) in download_sra_data.py.

            Run download_sra_data.py to download SRA data using fasterq-dump command.

    Notes:

        Ensure proper installation of SRA-toolkit for downloading SRA data.

        Adjust the download limit parameter in download_sra_data.py according to memory constraints and download requirements.


#### data_conversion_helper_functions/

    - convert_quantsf_to_csv.py
    - create_expression_matrix.py
    - create_samplesheet_csv.py
    - divide_samplesheet_into_batches.py
    - process_expression_matrix.py
    - rename_quant_output_and_move_to_dir.py
    - zip_fasta_files.py



#### median_expression_files/
    - rna_expression_chlamydomonas_reinhardtii.csv

#### quant_files/

##### processed/
    - chlamydomonas_reinhardtii.csv

##### raw/
    - chlamydomonas_reinhardtii/csv_files/
    - chlamydomonas_reinhardtii/sf_files/



#### test/
    - quant_test.csv
    - quant_test.sf

#### output_srx_srr.csv
#### requirements.txt
#### rna_extraction.py
#### rnaseq_params.yaml
#### run_nfcore_rnaseq_pipeline.py
#### sratoolkit.tar.gz



### tests/
#### test_dna/
#### test_rna/
#### test_main.py


### tutorials/

### visualisations/

### dataset_integration.py

### main.py

### requirements.txt

### species_ids.csv

## Running the Tests
TBC

## Time and Space Complexity
TBD

## Acknowledgments
Credits to contributors, funding organizations, or any third-party tools or datasets used.

## References
Links to the public databases, bioinformatics pipelines, and any other external references used in the project.
