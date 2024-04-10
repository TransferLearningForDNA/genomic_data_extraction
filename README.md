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
- Merge genomic and transcriptomic data tables by transcript ID.

[//]: # (### 3. Data Preparation for Machine Learning:)

[//]: # ()
[//]: # (- Discount irrelevant genes &#40;low expression&#41;.)

[//]: # (- Pad remaining promoters and terminators to standardise length.)

[//]: # (- Pad all UTRs to the same length to ensure consistency.)

[//]: # (- Drop genes with incomplete regulatory sequences.)

[//]: # (- Combine all sequences &#40;with equal length&#41; into a unified dataset.)

[//]: # (- One-Hot Encode &#40;OHE&#41; and stack sequence data for machine learning model compatibility.)


[//]: # (## Table of Contents)

## Installation

### Prerequisites
Before you begin the setup process, ensure you have the following prerequisites installed on your system:
1. This repository runs on **python version 3.10**. Ensure you have this installed.
2. The nf-core/rnaseq pipeline requires **Conda**. If you do not have Conda installed, we recommend installing **Miniconda**.

### Software Dependencies

**NOTE**: This repository requires two virtual environments for setup: a general `venv` for overall software dependencies, and a `conda` environment specific to the nf-core/rnaseq pipeline.
You can create the conda environment later, just before you run the nf-core/rnaseq pipeline. Refer back to these instructions at that time.

### _1. venv_
Create a virtual environment `venv` with **python version 3.10**.

Activate the venv:
```bash
source <venv_name>/bin/activate
```

Install the required depencencies:
```bash
pip install -r requirements.txt
```

### NCBI SRA Toolkit
The NCBI SRA Toolkit is required for the download and extraction of the mRNA data from NCBI SRA (fasterq-dump command-line tool).

Please follow the instructions below (run on terminal):
1. Download and extract the SRA Toolkit: 
```bash
curl --output sratoolkit.tar.gz https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-mac64.tar.gz
tar -vxzf sratoolkit.tar.gz
```
2. Temporary setup: Replace '<name_of_your_extracted_directory>' with the actual directory name (e.g., 'sratoolkit.3.0.10-mac-x86_64')
```angular2html
export PATH=$PATH:$PWD/<name_of_your_extracted_directory>/bin
```
3. For a permanent setup, add the PATH to your shell's profile script.
Replace '/<path_to_your_extracted_directory>/bin' with the full path and adjust the file name (.zshrc or .bash_profile) as necessary
```bash
echo 'export PATH=$PATH:/<path_to_your_extracted_directory>/bin' >> ~/.zshrc
```

### _2. conda_
### nf-core/rnaseq pipeline

The nf-core/rnaseq pipeline is used to extract gene expression levels from mRNA sequencing data.
We recommend using Conda with the bioconda channel for easy installation of the packages required by the Nextflow RNA sequencing workflow.

Run the following commands in your terminal:

1. Create a conda virtual environment. This will create a new virtual environment stored within your Miniconda directory structure.

```bash
conda create --name <name_of_your_env>
```

2. Activate the conda environment and install the following packages:

```bash
# Ensure your conda environment is activated before installing packages.
# Note: 
# - You may need to upgrade trim-galore with `conda upgrade trim-galore` if you encounter an issue with an obsolete `—cores` flag.
# - Ensure you specify version 1.3.0 for salmon to avoid compatibility issues with other dependencies.
conda activate
conda install trim-galore
conda install gffread
conda install fq
conda install -c conda-forge -c bioconda salmon=1.3.0
```

  
## Usage

ATTENTION: Pipeline run in separate steps. Plan sufficient storage (large files, especially fastq files)! Might have to run in batches.
TAILORED USE: specific species guidelines

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
