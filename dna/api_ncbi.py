import os
from pprint import pprint
import ncbi.datasets.openapi
from ncbi.datasets.openapi.api import genome_api

# Retrieve the API key from the environment variable
ncbi_api_key = os.getenv('NCBI_API_KEY')
if ncbi_api_key is None:
    raise EnvironmentError("NCBI API KEY not found. Please set the environment variable.")


configuration = ncbi.datasets.openapi.Configuration()
configuration.api_key['ApiKeyAuthHeader'] = ncbi_api_key

with ncbi.datasets.openapi.ApiClient(configuration) as api_client:
    api_instance = genome_api.GenomeApi(api_client)

    help(api_instance.download_assembly_package)

    # taxon_id = 130081  # Replace with the desired taxon ID
    # include_data_types = ["genome", "gff3"]  # Specify data types to include
    #
    # try:
    #     response = api_instance.download_assembly_package(taxon_id, include_data_types=include_data_types)
    #     # Process the response, which contains the downloaded data
    # except ncbi.datasets.openapi.ApiException as e:
    #     print(f"Exception when calling GenomeApi: {e}\n")
