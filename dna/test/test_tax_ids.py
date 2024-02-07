import requests, sys


def test_tax_ids():
    true_tax_id = '9606'

    server = "https://rest.ensembl.org"
    ext = "/taxonomy/id/Homo sapiens?"

    r = requests.get(server + ext, headers={"Content-Type": "application/json"})

    if not r.ok:
        r.raise_for_status()
        sys.exit()

    decoded = r.json()
    assert decoded['id'] == true_tax_id
