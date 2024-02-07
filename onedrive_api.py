import os
import logging
from azure.identity import InteractiveBrowserCredential
from msgraph.core import GraphClient
#from msgraph.core.exceptions import GraphError

# Use environment variables for sensitive information
CLIENT_ID = '8b4be9a3-e32e-4b8d-8889-463dde0b0b41'
TENANT_ID = '2b897507-ee8c-4575-830b-4f8267c3d307'
CLIENT_SECRET = '1b85dc9e-1d32-4510-a926-de09ed46cd96'
SCOPE = ['Files.ReadWrite.All']  # This might need to be adjusted based on the actual requirements

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialise Graph Client with Interactive Browser Credential
credentials = InteractiveBrowserCredential(client_id=CLIENT_ID, tenant_id=TENANT_ID)
client = GraphClient(credential=credentials, scopes=SCOPE)

def read_file_as_bytes(file_path):
    """
    Attempts to read a file's content and return it as bytes.
    Raises:
        IOError: If the file cannot be read.
    """
    with open(file_path, 'rb') as file:
        return file.read()

def download_file_from_onedrive(onedrive_file_id, local_path_to_save):
    """
    Downloads a file from OneDrive to a local path.
    # """
    # try:
    #     endpoint = f'/me/drive/items/{onedrive_file_id}/content'
    #     response = client.get(endpoint)
    #     if response.status_code == 200:
    #         with open(local_path_to_save, 'wb') as local_file:
    #             local_file.write(response.content)
    #         logging.info(f"File downloaded successfully to {local_path_to_save}")
    #     else:
    #         logging.error(f"Failed to download file. HTTP Error: {response.status_code}")
    # except GraphError as e:
    #     logging.error(f"Graph API Error: {e}")

    endpoint = f'/me/drive/items/{onedrive_file_id}/content'
    response = client.get(endpoint)
    if response.status_code == 200:
        with open(local_path_to_save, 'wb') as local_file:
            local_file.write(response.content)
        logging.info(f"File downloaded successfully to {local_path_to_save}")
    else:
        logging.error(f"Failed to download file. HTTP Error: {response.status_code}")


def download_files_from_onedrive(file_ids, local_directory_path):
    """
    Downloads multiple files from OneDrive based on their IDs and saves them to a local directory.

    Parameters:
    - file_ids (list): A list of unique identifiers of the files in OneDrive.
    - local_directory_path (str): The local file system directory where files will be saved.
    """
    for file_id in file_ids:
        local_path_to_save = os.path.join(local_directory_path, f"{file_id}.file_extension")  # Adjust file extension as necessary
        logging.info(f"Downloading file with ID {file_id}...")
        download_file_from_onedrive(file_id, local_path_to_save)


def upload_file_to_onedrive(onedrive_folder_id, local_file_path):
    """
    Uploads a local file to OneDrive.
    """
    try:
        file_content = read_file_as_bytes(local_file_path)
    except IOError as e:
        logging.error(f"Error reading file {local_file_path}: {e}")
        return
    
    file_name = os.path.basename(local_file_path)
    endpoint = f'/me/drive/items/{onedrive_folder_id}:/{file_name}:/content'

    # try:
    #     response = client.put(endpoint, content=file_content)
    #     if response.status_code == 201:
    #         logging.info(f"File uploaded successfully: {file_name}")
    #     else:
    #         logging.error(f"Failed to upload file. HTTP Error: {response.status_code}")
    # except GraphError as e:
    #     logging.error(f"Graph API Error: {e}")

    response = client.put(endpoint, data=file_content)
    if response.status_code == 201:
        logging.info(f"File uploaded successfully: {file_name}")
    else:
        logging.error(f"Failed to upload file. HTTP Error: {response.status_code}")

def upload_files_to_onedrive(onedrive_folder_id, local_directory_path):
    """
    Uploads all files from a local directory to a specified folder in OneDrive.

    Parameters:
    - onedrive_folder_id (str): The unique identifier of the folder in OneDrive.
    - local_directory_path (str): The path to the local directory containing files to be uploaded.
    """
    for file_name in os.listdir(local_directory_path):
        local_file_path = os.path.join(local_directory_path, file_name)
        if os.path.isfile(local_file_path):
            logging.info(f"Uploading {file_name}...")
            upload_file_to_onedrive(onedrive_folder_id, local_file_path)


def main():
    local_directory_for_upload = 'your_local_dir_with_files_to_upload_to_onedrive'
    onedrive_folder_id_for_upload = '0x01200074BF53252FD43242936F4421A798FF15'  # our shared folder
    upload_files_to_onedrive(onedrive_folder_id_for_upload, local_directory_for_upload)

    # local_directory_for_download = 'path_where_to_store_downloaded_files'
    # file_ids_to_download = ['onedrive_file_id_1', 'onedrive_file_id_2']  # List of file IDs to download
    # download_files_from_onedrive(file_ids_to_download, local_directory_for_download)

if __name__ == "__main__":
    main()
