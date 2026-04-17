# tools/openfda.py
import requests

BASE = 'https://api.fda.gov/drug'

def get_label_interactions(drug_name: str) -> str | None:
    """Pull drug_interactions field from FDA label. Returns text or None."""
    try:
        for field in ['openfda.generic_name', 'openfda.brand_name', 'drug_interactions']:
            r = requests.get(
                f'{BASE}/label.json?search={field}:"{drug_name}"&limit=1',
                timeout=8
            )
            if r.status_code == 200:
                results = r.json().get('results', [])
                if results:
                    interactions = results[0].get('drug_interactions', [])
                    if interactions:
                        return interactions[0]
        return None
    except Exception:
        return None

def get_adverse_event_count(drug_a: str, drug_b: str) -> int:
    """Returns FDA adverse event report count for a drug pair. -1 on error."""
    try:
        query = f'patient.drug.medicinalproduct:"{drug_a}"+AND+patient.drug.medicinalproduct:"{drug_b}"'
        r = requests.get(
            f'{BASE}/event.json?search={query}&limit=1',
            timeout=8
        )
        if r.status_code == 404:
            return 0
        r.raise_for_status()
        return r.json()['meta']['results']['total']
    except Exception:
        return -1
