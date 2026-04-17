# tools/rxnorm.py
import requests

RXNORM_BASE = 'https://rxnav.nlm.nih.gov/REST'

def normalize_medication(name: str) -> str | None:
    """
    Resolve a drug name (brand or generic) to its canonical generic name.
    Returns None if the name cannot be resolved.
    Examples: 'Tylenol' -> 'acetaminophen', 'Advil' -> 'ibuprofen'
    """
    name = name.strip()
    if not name:
        return None
    try:
        r = requests.get(
            f'{RXNORM_BASE}/rxcui.json',
            params={'name': name, 'search': 1},
            timeout=8
        )
        r.raise_for_status()
        ids = r.json().get('idGroup', {}).get('rxnormId', [])
        if not ids:
            return None
        rxcui = ids[0]

        r2 = requests.get(
            f'{RXNORM_BASE}/rxcui/{rxcui}/properties.json',
            timeout=8
        )
        r2.raise_for_status()
        return r2.json().get('properties', {}).get('name', '').lower() or None
    except Exception:
        return None
