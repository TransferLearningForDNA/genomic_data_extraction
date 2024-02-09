import requests, sys


def test_tax_ids():
    # true_tax_id = '9606'
    true_tax_id = '559292'
    # true_tax_id = '280699'

    server = "https://rest.ensembl.org"
    # ext = "/taxonomy/id/Homo sapiens?"
    ext ="/taxonomy/id/Saccharomyces cerevisiae?"
    # ext = "taxonomy/id/Cyanidioschyzon merolae?"

    r = requests.get(server + ext, headers={"Content-Type": "application/json"})

    if not r.ok:
        r.raise_for_status()
        sys.exit()

    decoded = r.json()
    print(repr(decoded))
    assert decoded['id'] == true_tax_id
