
def extract_rna_data():
    """ Extract RNA expression levels from RNA-seq data.

    Use NCBI SRA API to download fastq files and process the RNA-seq data using nf-core/rna-seq workflow
    to obtain the gene expression matrix. Calculate median expression levels and RSD.
    """

    # Extracting gene expression levels.

    # Use NCBI SRA API to download fastq files containing RNA-seq data.

    # RNA-seq processing workflow (nf-core/rnaseq)
    # Extract gene expression matrix (TPM): samples vs gene_id

    # TODO Calculate RSD and median expression
    # 1x Gene ID
    # 1x Median expressions of genes with RDS < 2

    pass