import os
import logging
from azure.identity import InteractiveBrowserCredential
from msgraph.core import GraphClient
from msgraph.core.exceptions import GraphError

# Use environment variables for sensitive information
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
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
    """
    try:
        endpoint = f'/me/drive/items/{onedrive_file_id}/content'
        response = client.get(endpoint)
        if response.status_code == 200:
            with open(local_path_to_save, 'wb') as local_file:
                local_file.write(response.content)
            logging.info(f"File downloaded successfully to {local_path_to_save}")
        else:
            logging.error(f"Failed to download file. HTTP Error: {response.status_code}")
    except GraphError as e:
        logging.error(f"Graph API Error: {e}")

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

    try:
        response = client.put(endpoint, content=file_content)
        if response.status_code == 201:
            logging.info(f"File uploaded successfully: {file_name}")
        else:
            logging.error(f"Failed to upload file. HTTP Error: {response.status_code}")
    except GraphError as e:
        logging.error(f"Graph API Error: {e}")

def main():
    local_download_path = 'path_where_to_store_downloaded_file'
    onedrive_file_id = 'onedrive_file_id_to_download'
    local_upload_path = 'path_to_local_file_for_upload'
    onedrive_folder_id = 'onedrive_folder_id_for_upload'

    download_file_from_onedrive(onedrive_file_id, local_download_path)
    upload_file_to_onedrive(onedrive_folder_id, local_upload_path)

if __name__ == "__main__":
    main()
