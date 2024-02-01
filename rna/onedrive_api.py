# see readme: https://github.com/microsoftgraph/msgraph-sdk-python

# note: need to figure out which Microsoft Azure authentication library to use.
# TODO: application or delegated permissions?
# TODO: test that this actually works for reading/writing files with our onedrive shared folder
# TODO: function signatures to fix

# Initialize a GraphServiceClient object to make requests against the service
# Example using sync credentials and delegated access.
import os
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient

# these IDs can be found on Microsoft Azure, in applications registered
CLIENT_ID = '8b4be9a3-e32e-4b8d-8889-463dde0b0b41'
TENANT_ID = '2b897507-ee8c-4575-830b-4f8267c3d307' # directory ID

credentials = DeviceCodeCredential(CLIENT_ID, TENANT_ID)
scopes = ['User.Read', 'Mail.Read']

client = GraphServiceClient(credentials=credentials, scopes=scopes)

# Make requests against the Onedrive service

# function to convert contents of files (e.g. fastq) to bytes (need it for writing)
def read_file_as_bytes(file_path):
    """
    Function to read a file and return its content as bytes.
    
    Parameters:
        file_path (str): The path to the file.
        
    Returns:
        bytes: Content of the file.
    """
    with open(file_path, 'rb') as file:
        file_content_in_bytes = file.read()
    return file_content_in_bytes

# function to read files / download locally from the shared Onedrive folder
def read_locally_file_from_onedrive(onedrive_file_id, local_path_to_save):
    """
    Function to read a file from OneDrive and save it locally with its original extension.
    
    Parameters:
        file_id (str): The ID of the file to read.
        local_path (str): The local directory where the file will be saved.
        
    Returns:
        None.
    """
    # Use GraphServiceClient to get the file metadata
    file_metadata = client.onedrive.drive.items[onedrive_file_id].get()
    
    # Extract file name and extension from the metadata
    file_name = file_metadata.name
    file_extension = os.path.splitext(file_name)[1]
    
    # Construct the local file path with the original file name and extension
    local_file_path = os.path.join(local_path_to_save, file_name)
    
    # Use GraphServiceClient to download the file content
    with open(local_file_path, 'wb') as local_file:
        client.onedrive.drive.items[onedrive_file_id].content.download(local_file)


# function to write files / upload to the shared Onedrive folder
def write_file_to_onedrive(onedrive_folder_path, file_name, local_file_path):
    """
    Function to write a file to a specific folder in OneDrive.
    
    Parameters:
        folder_path (str): The path to the folder where the file will be written.
        file_name (str): The name of the file to write.
        file_content (bytes): Content to be written to the file.
        
    Returns:
        None.
    """
    # convert the file content to bytes
    file_content_in_bytes = read_file_as_bytes(file_path)

    # Use GraphServiceClient to upload the file content to the specified folder
    file_path = f"{onedrive_folder_path}/{file_name}"
    new_file = client.onedrive.drive.root.itemWithPath(file_path).content.request().put(file_content_in_bytes)
    # new_file.id will return the ID of the file


# Example usage
# Read a file (given file ID from the URL in the Onedrive web browser) from a specific folder in Onedrive
local_path_to_save = 'local_path_where_we_want_to_store_the_file_downloaded_from_onedrive'
read_locally_file_from_onedrive('ONEDRIVE_FILE_ID', local_path_to_save)
# Write a file to a specific folder in OneDrive
local_file_path = 'local_path_to_file_we_want_to_upload_to_onedrive'
write_file_to_onedrive('ONEDRIVE_FOLDER_PATH', 'FILE_NAME', local_file_path)
