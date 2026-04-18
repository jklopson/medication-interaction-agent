# tools/pubchem.py
import requests

BASE = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'

def get_pubchem_data(drug_name: str) -> str | None:
    """
    Fetch safety and interaction-relevant data from PubChem.
    Returns plain text summary or None.
    """
    try:
        # Step 1: get CID for drug name
        r = requests.get(
            f'{BASE}/compound/name/{requests.utils.quote(drug_name)}/JSON',
            timeout=8
        )
        if r.status_code != 200:
            return None
        cid = r.json()['PC_Compounds'][0]['id']['id']['cid']

        # Step 2: fetch safety/bioactivity description
        r2 = requests.get(
            f'{BASE}/compound/cid/{cid}/description/JSON',
            timeout=8
        )
        if r2.status_code != 200:
            return None

        descriptions = r2.json().get('InformationList', {}).get('Information', [])
        for item in descriptions:
            desc = item.get('Description', '')
            if len(desc) > 100:
                return desc[:1500]
        return None
    except Exception:
        return None