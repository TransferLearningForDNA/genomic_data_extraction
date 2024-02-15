def merge_datasets():
    """ Merge DNA and RNA data by gene ID. """

    # TODO Merge DNA and RNA data by gene_id

    # TODO Store final dataset in One Drive
    pass


# def merge_datasets(species_name):
#     """function to merge DNA and RNA datasets for a given species by gene ID."""
#     bucket_name = 's3-bucket-name'  # change after s3 bucket is made
#     dna_file_key = f'datasets/{species_name}_DNA.csv'  # here i am assuming the file is csv
#     rna_file_key = f'datasets/{species_name}_RNA.csv'
#
#     # downloading files from S3
#     download_s3_file(bucket_name, dna_file_key, 'dna_data.csv')
#     download_s3_file(bucket_name, rna_file_key, 'rna_data.csv')
#
#     # read datasets into pandas DataFrames
#     dna_df = pd.read_csv('dna_data.csv')
#     rna_df = pd.read_csv('rna_data.csv')
#
#     # merge datasets on gene ID
#     merged_df = pd.merge(dna_df, rna_df, on='gene_id')
#     merged_df.to_csv(f'merged_{species_name}_data.csv', index=False)
#     return merged_df
#
#
# merged_data = merge_datasets('dummy_species')
