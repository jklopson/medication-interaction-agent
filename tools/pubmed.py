# tools/pubmed.py
import requests

BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'

def get_pubmed_abstracts(drug_a: str, drug_b: str, max_results: int = 3) -> str | None:
    """
    Search PubMed for studies on a drug pair interaction.
    Returns concatenated abstracts or None.
    """
    try:
        # Step 1: search for relevant PMIDs
        search_term = f'"{drug_a}"[Title/Abstract] AND "{drug_b}"[Title/Abstract] AND interaction[Title/Abstract]'
        r = requests.get(
            f'{BASE}/esearch.fcgi',
            params={
                'db': 'pubmed',
                'term': search_term,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'
            },
            timeout=8
        )
        if r.status_code != 200:
            return None

        ids = r.json().get('esearchresult', {}).get('idlist', [])
        if not ids:
            return None

        # Step 2: fetch abstracts for those PMIDs
        r2 = requests.get(
            f'{BASE}/efetch.fcgi',
            params={
                'db': 'pubmed',
                'id': ','.join(ids),
                'rettype': 'abstract',
                'retmode': 'text'
            },
            timeout=8
        )
        if r2.status_code != 200:
            return None

        text = r2.text.strip()
        return text[:2000] if text else None
    except Exception:
        return None