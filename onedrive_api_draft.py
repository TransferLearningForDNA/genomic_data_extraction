# see readme: https://github.com/microsoftgraph/msgraph-sdk-python

# note: need to figure out which Microsoft Azure authentication library to use.
# TODO: application or delegated permissions?
# TODO: test that this actually works for reading/writing files with our onedrive shared folder
# TODO: function signatures to fix

# Initialise a GraphServiceClient object to make requests against the service
# Example using sync credentials and delegated access.
import os
#from azure.identity import DeviceCodeCredential  #suitable for applications that can't use a web browser to sign in to Azure ID
from azure.identity import InteractiveBrowserCredential #suitable for scripts and applications running on devices with web browser
from msgraph.core import GraphClient
from msgraph.core.exceptions import GraphError

# these IDs can be found on Microsoft Azure, in applications registered
CLIENT_ID = '8b4be9a3-e32e-4b8d-8889-463dde0b0b41'
TENANT_ID = '2b897507-ee8c-4575-830b-4f8267c3d307' # directory ID
SCOPE = ['Files.ReadWrite.All']  # need to adjust this


# Initialise Graph Client with Interactive Browser Credential
credentials = InteractiveBrowserCredential(client_id=CLIENT_ID, tenant_id=TENANT_ID)
client = GraphClient(credential=credentials, scopes=SCOPE)
# Make requests against the Onedrive service

# function to convert contents of files (e.g. fastq) to bytes (need it for writing)
def read_file_as_bytes(file_path):
    """
Reads a file from the given path and returns its content as bytes.

    Parameters:
    - file_path (str): The full path to the file to be read.

    Returns:
    - bytes: The content of the file as bytes.
    """
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def download_file_from_onedrive(onedrive_file_id, local_path_to_save):
    """
    Downloads a file from OneDrive based on its ID and saves it to a local path.

    Parameters:
    - onedrive_file_id (str): The unique identifier of the file in OneDrive.
    - local_path_to_save (str): The local file system path where the file will be saved.
    """
    try:
        endpoint = f'/me/dri
        ve/items/{onedrive_file_id}/content'
        response = client.get(endpoint)
        if response.status_code == 200:
            with open(local_path_to_save, 'wb') as local_file:
                local_file.write(response.content)
        else:
            print(f"Failed to download file. HTTP Error: {response.status_code}")
    except GraphError as e:
        print(f"Graph API Error: {e}")


def upload_file_to_onedrive(onedrive_folder_id, local_file_path):
    """
    Uploads a local file to a specified folder in OneDrive.

    Parameters:
    - onedrive_folder_id (str): The unique identifier of the folder in OneDrive where the file will be uploaded.
    - local_file_path (str): The full path to the local file to be uploaded.
    """
    file_content = read_file_as_bytes(local_file_path)
    if file_content is None:
        print("Failed to read local file.")
        return
    
    file_name = os.path.basename(local_file_path)
    endpoint = f'/me/drive/items/{onedrive_folder_id}:/{file_name}:/content'

    try:
        response = client.put(endpoint, content=file_content)
        if response.status_code == 201:
            print(f"File uploaded successfully: {file_name}")
        else:
            print(f"Failed to upload file. HTTP Error: {response.status_code}")
    except GraphError as e:
        print(f"Graph API Error: {e}")


# Example usage
def main():
    """
    Main function demonstrating the use of the above functions.
    """
    # IDs and paths
    local_download_path = 'path_where_to_store_downloaded_file'
    onedrive_file_id = 'onedrive_file_id_to_download'
    local_upload_path = 'path_to_local_file_for_upload'
    onedrive_folder_id = 'onedrive_folder_id_for_upload'

    # Download a file from OneDrive
    download_file_from_onedrive(onedrive_file_id, local_download_path)

    # Upload a file to OneDrive
    upload_file_to_onedrive(onedrive_folder_id, local_upload_path)

if __name__ == "__main__":
    main()




