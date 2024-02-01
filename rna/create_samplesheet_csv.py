import os
import csv

# DEPECRATED LIBRARY: investigating another approach for the API
import onedrivesdk 
from onedrivesdk.helpers import GetAuthCodeServer
from onedrivesdk.helpers.resource_discovery import ResourceDiscoveryRequest

# TODO: specify the path to the folder containing the sample fastq files

# if saved in a local directory
# folder_path = '/path/to/your/folder'

# if saved in (Imperial) OneDrive (#TODO)
redirect_uri = 'http://localhost:8080'
client_id = '8b4be9a3-e32e-4b8d-8889-463dde0b0b41'
client_secret = '1b85dc9e-1d32-4510-a926-de09ed46cd96' 
discovery_uri = 'https://graph.microsoft.com/v1.0/me'
auth_server_url = 'https://login.microsoftonline.com/common/oauth2/authorize'
auth_token_url = 'https://login.microsoftonline.com/common/oauth2/token'

http = onedrivesdk.HttpProvider()
auth = onedrivesdk.AuthProvider(http,
                                client_id,
                                auth_server_url=auth_server_url,
                                auth_token_url=auth_token_url)
auth_url = auth.get_auth_url(redirect_uri)
code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
auth.authenticate(code, redirect_uri, client_secret, resource=discovery_uri)
# If you have access to more than one service, you'll need to decide
# which ServiceInfo to use instead of just using the first one, as below.
service_info = ResourceDiscoveryRequest().get_service_info(auth.access_token)[0]
auth.redeem_refresh_token(service_info.service_resource_id)
client = onedrivesdk.OneDriveClient(service_info.service_resource_id + '/_api/v2.0/', auth, http)

# Specify the folder ID (replace 'folder_id' with the actual folder ID)
folder_id = 'folder_id'  # TODO: edit this to point to our shared folder with the files (you can find it in the URL on Onedrive)

# List files in the specified folder
items_in_folder = client.item(drive='me', id=folder_id).children.get()
# for item in items_in_folder:
#     print(f"File: {item.name}, Size: {item.size} bytes")

# list all the files in the folder path
file_paths = []
# Iterate over the files in the specified folder
for item in items_in_folder:
    file_paths.append(os.path.join(folder_path, item.name))
# if the files are locally stored
#files = [file for file in os.listdir(folder_path) if file.endswith(file_extension)]

# preprocess all samples across all our species (one csv file)
# TODO: update this to be one csv file PER species

# iterate over the fastq files to populate the dict containing the fastq filepath(s)
# of each sample (across all species we are considering/saved in the folder)
sample_fastq_files_path_dict = dict()
for sample_fastq_file in file_paths:

    # get the absolute file path
    file_path = os.path.join(folder_path, sample_fastq_file)

    sample_name_key = sample_fastq_file[:-8]  # naming convention = samplename_1.fastq

    if sample_name_key in sample_fastq_files_path_dict:
        sample_fastq_files_path_dict[sample_name_key].append(file_path)
        # sort by fastq file number
        sample_fastq_files_path_dict[sample_name_key] = sorted(
            sample_fastq_files_path_dict[sample_name_key],
            key=lambda fastq_filename: fastq_filename[-7]
        )
    else:
        sample_fastq_files_path_dict[sample_name_key] = [file_path]

# populate the data structure that will hold the rows of the csv file
strandedness = 'auto'  # using default parameter value for now
data = []   # list of sublists (where each sublist is a sample/row in the dataset)
for sample_name, fastq_files_paths_list in sample_fastq_files_path_dict:

    if len(fastq_files_paths_list) == 1:
        fastq_file1_path = fastq_files_paths_list[0]
        fastq_file2_path = ''
    else:
        assert len(fastq_files_paths_list) == 2  # max number of fastq files per sample
        fastq_file1_path = fastq_files_paths_list[0]
        fastq_file2_path = fastq_files_paths_list[1]

    sample_row_data = [sample_name, fastq_file1_path, fastq_file2_path, strandedness]
    data.append(sample_row_data)

# create the samplesheet csv file (input to the nextflow nfcore/rnaseq pipeline)
# columns of the samplesheet csv file
header = ['sample', 'fastq_1', 'fastq_2', 'strandedness']
with open("samplesheet.csv", "w") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)
    writer.writerows(data)
