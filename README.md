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
- Merge genomic and transcriptomic data tables by gene ID.

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
Replace '<path_to_your_extracted_directory>' with the full path and adjust the file name (.zshrc, .bashrc or .bash_profile) as necessary.
```bash
echo 'export PATH=$PATH:/<path_to_your_extracted_directory>/bin' >> ~/.zshrc
```

### _2. conda_
### nf-core/rnaseq pipeline

The nf-core/rnaseq pipeline is used to extract gene expression levels from mRNA sequencing data.
We recommend using Conda with the bioconda channel for easy installation of the packages required by the Nextflow RNA sequencing workflow.

1. Create a conda virtual environment. This will create a new virtual environment stored within your Miniconda directory structure.

```bash
conda create --name <name_of_your_env>
```

2. Activate the conda environment and install the following packages:

```bash
# Ensure your conda environment is activated before installing packages.
conda activate <name_of_your_env>

# Note: 
# - You may need to upgrade trim-galore with `conda upgrade trim-galore` if you encounter an issue with an obsolete `—cores` flag.
# - Specify version 1.3.0 for salmon to avoid compatibility issues with other dependencies.
conda install trim-galore
conda install gffread
conda install fq
conda install -c conda-forge -c bioconda salmon=1.3.0
conda install nextflow
```

3. If you plan to use this environment on another machine or share it, create a YML file that lists all the installed packages.
Removing build information from the YML file makes the environment more portable across different operating systems (e.g. MacOS -> Linux).

```bash
# Export environment to yml
# Optional flag for removing build strings: --no-build
conda <name_of_activated_conda_env> export --no-build > <env_file_name>.yml

# Recreate environment from yml file
conda env -f <env_file_name>.yml
```


  
## Usage

**NOTE**: The pipeline operates in discrete steps and handles large datasets, notably fastq files, which may require significant storage. Consider the following recommendations to ensure smooth operation:

- **Storage Planning**: Anticipate the need for substantial storage capacity. You may need to execute some sections of the pipeline in batches to manage space efficiently.

- **Time Expectations**: Downloading DNA and mRNA data, along with preprocessing of fastq files, can be time-consuming. Plan accordingly.

- **Performance Optimisation**: We advise running the DNA extraction from Ensembl database on High-Performance Computing (HPC) systems.
We also recommend ensuring that your machine has enough RAM to handle the computational load of the nf-core/rnaseq pipeline.
You can use tools such as `tmux` to process tasks in parallel and reduce runtimes. The pipeline is also compatible with various HPC execution schedulers.
Please find more information in the nextflow documentation: https://nf-co.re/docs/usage/configuration.


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
`<output_directory>`: Specifies the path to the directory where the RNA-seq data will be saved. Ensure this directory exists and is writable. Please provide the full path to avoid errors.
`<file_number_limit>`: Specifies the maximum number of files to be downloaded (i.e. How many RNA-seq experiment run samples do you wish to download?).
Defaults to 10 as a precaution due to large storage requirements.

```bash
# file_number_limit (int) argument is optional (defaults to 10)
python main.py download_rna_data <output_directory> <file_number_limit>
```

**Important notes**:
- Ensure the NCBI SRA Toolkit is correctly installed (see Installation instructions).
- The species_ids.csv file must be correctly formatted and located in your main repository directory.
- Ensure the output directory has sufficient storage space for the downloaded data.
As fastq files can be large, it's advisable to download the files per species or in batches to manage disk space effectively.

#### 2. Run nf-core/rnaseq pipeline to obtain gene expression matrix _(per species)_

- Once downloaded, zip the fastq files by running the following commands:

```bash
# Go to the output folder directory (e.g. species-specific) containing the fastq files you would like to process. 
cd <fastq_files_directory>
# Convert all files from .fastq to .fastq.gz
# optional flag '-k' to keep original files (avoids re-downloading in case the zipping corrupts the files)
gzip -k *

# OR use rna/data_conversion_helper_functions/zip_fasta_files.py ??
#zip_files(directory)
```

- The pipeline requires FASTA and GFF3 reference genome files. Manually download these from the Ensembl website (it should take a few seconds).
  - Species Ensembl page -> Gene annotation section
  - Click on FASTA (takes you to another page e.g. https://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/release-58/fasta/chlamydomonas_reinhardtii/)
    1. Under `dna/` download the file ending in `.dna.toplevel.fa.gz`
    2. Under `cdna/` download the file ending in `.cdna.all.fa.gz`.
  - Click on GFF3 (take you to another page e.g. https://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/release-58/gff3/chlamydomonas_reinhardtii/). Download the file ending in `.gff3.gz`. 
    - IMPORTANT: Manually edit the extension from `.gff3.gz` to `.gff.gz` (otherwise the rnaseq pipeline does not recognise the file). In the terminal, type: `mv <name_of_file.gff3.gz> <name_of_file.gff.gz>.

- Ensure a conda environment has been created containing all required dependencies for the nf-core/rnaseq pipeline (see Installation section).

- Activate the conda environment and create the salmon index file (run this only once per species).

```bash
# If conda is not activated run:
# source ~/.zshrc (or .bashrc)
conda activate <virtual_env_name>

# transcript_fasta file: .cdna.all.fa.gz
salmon index -t <path/to/the/transcript_fasta/file> -i <path/to/directory/to/store/salmon_index/files> 
```

- Create a samplesheet csv file for a species used as input to the nf-core/rna-seq pipeline.

```bash
# Samplesheet csv file with columns: "sample", "fastq_1" (full path), "fastq_2", "strandedness
# rna/data_conversion_helper_functions/create_samplesheet_csv.py
create_samplesheet_for_one_species(species_name,
                                   local_dir_path_with_fastq_files_for_one_species,
                                   local_dir_path_to_save_samplesheets)
                                     
# divide_sampleshet_into_batches.py?? (optional?)
```

- Change the file paths in the provided template YAML file (`rna/rnaseq_params.yaml`), which specifies the pipeline parameters. Particularly for `input` (), `outdir` (directory to store the ), `fasta` (), `gff` (), `salmon_index` (), `transcript_fasta` ().

- Create the yaml for each species, batch? (how) Input csv

- run the pipeline (per species or in batches).

```bash
# If conda is not activated run:
# source ~/.zshrc (or .bashrc)
conda activate <virtual_env_name>

# Run the pipeline:
nextflow run nf-core/rnaseq -params file /path/to/yaml/with/params/to/rnaseq/pipeline -r 3.14.0 --max_cpus <integer_max_cpus_on_machine> --max_memory <float_max_memory_on_machine>.GB

# rna/run_nfcore_rnaseq_pipeline.py?

# Extract the necessary quant.sf files from the pipeline's output, add the sample name and move to species-specific folder
# rna/data_conversion_helper_functions/rename_quant_output_and_move_to_dir.py
rename_and_move_files(source_dir, destination_dir)
```

- WARNING: Possible error when running the nf-core rnaseq pipeline, but not a problem if quant.sf files have been created.
- WARNING: Also possible faulty samples -> error. No output will be saved -> run in batched (remove sample from input csv)

#### 3. Process expression data _(all species)_
- Run the following command to process raw transcriptomic data (quant.sf files obtained from the nf-core/rnaseq pipeline), filter transcripts with RSD < 2 and obtain the median expression (length scaled TPM) of each gene.

```bash
python3.10 main.py process_rna_expression
```

### Final dataset

#### 1. Merge processed genomic and transcriptomic data

```bash
python3.10 main.py merge_datasets
```

The final dataset csv files can be found under `merged_csv_files` and will be named `merged_<species_name>`.

Here is an example of what such a file will look like (only a snippet of the data for one gene is depicted):

```text
ensembl_gene_id,transcript_id,promoter,utr5,cds,utr3,terminator,AAA,AAC,AAG,AAT,ACA,ACC,ACG,ACT,AGA,AGC,AGG,AGT,ATA,ATC,ATG,
ATT,CAA,CAC,CAG,CAT,CCA,CCC,CCG,CCT,CGA,CGC,CGG,CGT,CTA,CTC,CTG,CTT,GAA,GAC,GAG,GAT,GCA,GCC,GCG,GCT,GGA,GGC,GGG,GGT,GTA,GTC,
GTG,GTT,TAA,TAC,TAG,TAT,TCA,TCC,TCG,TCT,TGA,TGC,TGG,TGT,TTA,TTC,TTG,TTT,cds_length,utr5_length,utr3_length,utr5_gc,cds_gc,
utr3_gc,cds_wobble2_gc,cds_wobble3_gc,median_exp
CMA001C,CMA001CT,ATGTAAAAATACACTCCACGGAGGATTTTTCGGTAAATTGGGTGAAACGTGAGGAAGTCTCCGATTGTGAAAGTATTCTACGCGGATCATTGGTCTGCGCCAGCCC
TGCAAATGCATGGTGATGCAAGGCTTGCCAGCGGCAGTTGAAATACATGCTCAAAGCTTACGCCGAATAAGGTTAGATGAAAAAGTGACTTACGAGTTCCCACTTCGTGGGTTGATAGCTGAA
[...]
0.0152838427947598,0.0,0.0349344978165938,0.029475982532751,0.0054585152838427,0.0010917030567685,0.0207423580786026,
0.0163755458515283,0.0240174672489082,2748,,4.0,,0.5505822416302766,0.5,0.537117903930131,0.601528384279476,34.8769964989974
```




## Directory Structure
Description of the repository's organization, explaining what each file and folder contains.

- `dna/`: Contains scripts and data for DNA extraction and feature analysis.
  - `dna_extraction.py`: Extracts and processes genomic data from Ensembl database.
  - `dna_feature_extraction.py`: Analyses DNA sequences to extract features ( e.g.codon frequencies, lengths, GC content).
  - `ensembl_api.py`: Interacts with the Ensembl API for data retrieval.
  - `gene_lists/`: Directory containing lists of gene stable IDs for each species.
  - `csv_files/`: Directory containing csv files with raw (temporary) or processed DNA data. 


- `rna/`: Scripts and resources for RNA data processing and analysis.
    - `rna_extraction.py`: Script for RNA sequence extraction (download & processing).
    - `rna_download_logic/`: Logic for downloading RNA data from NCBI SRA.
    - `data_conversion_helper_functions/`: Helper scripts for data format conversion and expression matrix processing.
    - `quant_files/`: Contains raw and processed nf-core/rnaseq pipeline output data.
      - `processed/`: Contains expression matrix csv files for each species (length-scaled TPM of all RNA-seq samples).
      - `raw/`: Contains folders for each species within which are stored `sf_files/` (raw nf-core/rnaseq Salmon quantification output files) and `csv_files/` (converted format).
    - `media_expression_files/`: Contains csv files with calculated median expression of selected transcripts.
    - `rnaseq_params.yaml`: Template YAML file used to run the nf-core/rnaseq pipeline.


- `dataset_integration.py`: Integrates DNA and RNA datasets.
- `main.py`: The main script to run analyses.
- `requirements.txt`: Required Python packages for the repository.
- `species_ids.csv`: CSV file containing s`pecies identifiers used in analysis.
- `rnaseqpipeline_conda_env.yml`


- `tests/`: Unit tests for DNA and RNA processing scripts.
- `tutorials/`: Jupyter notebooks.
- `visualizations/`: Scripts for exploratory data analysis (EDA) visualisations.


For detailed usage and function descriptions, refer to the corresponding script's documentation.


## Running the Tests
TBC

## Time and Space Complexity
TBD

## Acknowledgments
Credits to contributors, funding organizations, or any third-party tools or datasets used.

## References
Links to the public databases, bioinformatics pipelines, and any other external references used in the project.
