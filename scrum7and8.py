# implementation of simple skeleton code to merge the datasets by the gene ID column: use a “dummy species” to write the code
# dummy data is used so that some sort of skeleton code is ready with the basic layout to add in processed data later on
# NOTE: code has to be modified after S3 bucket is implemented and processed code is received.

# ticket 2 code:
#for each species, retrieve the DNA and RNA datasets from S3
#code to merge the datasets by the gene ID column: use a “dummy species” to write the code

import pandas as pd
import boto3


def download_s3_file(bucket_name, file_key, local_file_name): # change these names after s3 bucket is made
    """download a file from an S3 bucket."""
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, file_key, local_file_name)

def merge_datasets(species_name):
    """function to merge DNA and RNA datasets for a given species by gene ID."""
    bucket_name = 's3-bucket-name' # change after s3 bucket is made
    dna_file_key = f'datasets/{species_name}_DNA.csv' # here i am assuming the file is csv
    rna_file_key = f'datasets/{species_name}_RNA.csv'

    # downloading files from S3
    download_s3_file(bucket_name, dna_file_key, 'dna_data.csv')
    download_s3_file(bucket_name, rna_file_key, 'rna_data.csv')

    # read datasets into pandas DataFrames
    dna_df = pd.read_csv('dna_data.csv')
    rna_df = pd.read_csv('rna_data.csv')

    # merge datasets on gene ID
    merged_df = pd.merge(dna_df, rna_df, on='gene_id')
    merged_df.to_csv(f'merged_{species_name}_data.csv', index=False)
    return merged_df

merged_data = merge_datasets('dummy_species')


# ticket 3 code
# store the merged datasets that we obtained in the previous step in S3
# remove the original datasets from S3 if not enough space - optional


import boto3
from botocore.exceptions import NoCredentialsError

def upload_file_to_s3(local_file_name, bucket_name, s3_file_name): # again, change these after s3 bucket is made
    """upload a file to an S3 bucket."""
    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_file_name, bucket_name, s3_file_name)
        print(f"File {local_file_name} uploaded to {bucket_name}/{s3_file_name}.")
        return True
        # i have added two exceptions for the only errors that I think we will encounter with this function
    except FileNotFoundError:
        print("file not found")
        return False
    except NoCredentialsError:
        print("credentials not available")
        return False

def delete_file_from_s3(bucket_name, file_key):
    """function to delete a file from an S3 bucket. only applicable if there is not enough space"""
    s3 = boto3.client('s3')
    s3.delete_object(Bucket=bucket_name, Key=file_key)
    print(f"File {file_key} deleted from {bucket_name}.")

def store_merged_data_and_cleanup(species_name, merged_file_name):
    """function to upload the merged dataset to S3 and delete original datasets if needed"""
    bucket_name = 's3-bucket-name'

    # Upload the merged dataset
    merged_file_key = f'datasets/merged_{species_name}.csv'
    if upload_file_to_s3(merged_file_name, bucket_name, merged_file_key):
        # if upload is successful, delete the original datasets - do this if there is not enough space, but this is recommended. maybe store the original datasets somewhere else as a backup
        dna_file_key = f'datasets/{species_name}_DNA.csv'
        rna_file_key = f'datasets/{species_name}_RNA.csv'
        delete_file_from_s3(bucket_name, dna_file_key)
        delete_file_from_s3(bucket_name, rna_file_key)

store_merged_data_and_cleanup('dummy_species', 'merged_dummy_species_data.csv')
