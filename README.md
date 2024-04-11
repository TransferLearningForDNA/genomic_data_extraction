# Expression Prediction Data Preprocessing Pipeline

## Overview
This repository contains a pipeline for collecting, processing, and storing DNA and mRNA expression
profile data of given species from publicly available genetic databases.

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

[//]: # (Instructions on how to use the pipeline &#40;starting from the *outputs* of the RNA sequencing workflow&#41;, including commands and expected inputs/outputs.)

[//]: # (ATTENTION: Pipeline run in separate steps. Plan sufficient storage &#40;large files, especially fastq files&#41;! Might have to run in batches.)

[//]: # (Recommended to back up data somewhere. Download of DNA and mRNA data, and the preprocessing of fastq files can take a long time!)

[//]: # (nfcore/rnaseq RAM usage ?! Advice to parallelize run on HPC, powerful machines &#40;not everything possible&#41;.)

**ATTENTION**: The pipeline operates in discrete steps and handles large datasets, notably fastq files, which may require significant storage. Consider the following recommendations to ensure smooth operation:

- **Storage Planning**: Anticipate the need for substantial storage capacity. You may need to execute the pipeline in batches to manage space efficiently.

- **Data Backup**: Regularly back up your data to a secure location, especially before initiating large downloads or preprocessing tasks.

- **Time Expectations**: Downloading DNA and mRNA data, along with preprocessing of fastq files, can be time-consuming. Plan accordingly.

- **Performance Optimization**: For optimal performance, particularly given the nf-core/rnaseq pipeline's RAM demands, we advise running the pipeline on High-Performance Computing (HPC) systems or powerful machines. Parallelizing tasks where possible will significantly reduce runtimes.

[//]: # (TAILORED USE: specific species guidelines)

### Genomic data

#### 1. Get gene lists from Ensembl BioMart

- Go to Ensembl BioMart page and download the gene ID lists of desired species as TSV/.txt files (select species, select attribute Gene Stable ID and click 'Results').
https://www.ensembl.org/biomart/martview
- Store the files in the repository `dna/gene_lists/` folder. 

#### 2. Extract and process DNA data _(all species)_

Query genomic sequences from the Ensembl database and extract DNA components including:
- DNA sequences: promoter, utr5, cds, utr3 and terminator
- Codon frequencies in the CDS (coding sequence)
- Sequence lenghts: cds_length, utr5_length, utr3_length
- GC content: utr5_gc, cds_gc, utr3_gc, cds_wobble2_gc, cds_wobble3_gc

_Note:_ You might want to test this first with a small dataset e.g. `dna/gene_lists/homo_sapiens_genes_small.txt`.

- After you have added the desired files to `dna/gene_lists/` run the following command in the terminal.
```bash
python3.10 main.py extract_dna_data
```

- The obtained CSV files will be saved under `dna/csv_files` and named `ensembl_data_<species_name>.csv`.


### Expression data

#### 1. Download mRNA data from NCBI SRA _(all species, per species recommended)_

- Ensure a file named `species_ids.csv` is located in the main repository directory.
Please edit the example file provided in the repository with the desired species names and taxonomy IDs.
The csv file should contain columns `name` and `tax_id`.

- The following command uses NCBI SRA API to download fastq files for given species to the specified output_directory.
<output_directory>: Specifies the path to the directory where the RNA-seq data will be saved.
Ensure this directory exists and is writable. Please provide the full path to avoid errors.

```bash
python main.py download_rna_data <output_directory>
```

**Important Notes**:
- Ensure the NCBI SRA Toolkit is correctly installed (see Installation instructions).
- The species_ids.csv file must be correctly formatted and located in your main repository directory.
- Ensure the output directory has sufficient storage space for the downloaded data.
As fastq files can be large, it's advisable to download the files per species or in batches to manage disk space effectively and streamline the processing.

#### 2. Run nf-core/rnaseq pipeline to obtain gene expression matrix _(per species)_

#### 3. Process expression data _(all species)_

### Final dataset

#### 1. Merge processed genomic and transcriptomic data



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
