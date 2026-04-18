# agent/react_loop.py
import replicate, os, json
from dotenv import load_dotenv
from itertools import combinations
from tools.rxnorm import normalize_medication
from tools.openfda import get_label_interactions, get_adverse_event_count
from tools.pubchem import get_pubchem_data
from tools.pubmed import get_pubmed_abstracts
from agent.prompts import SYSTEM_PROMPT, format_tool_results
from agent.grader import has_sufficient_data

load_dotenv()
MODEL = os.getenv('GRANITE_MODEL')

def run(drug_a_raw: str, drug_b_raw: str) -> dict:
    # Step 1: normalize
    drug_a = normalize_medication(drug_a_raw) or drug_a_raw.lower().strip()
    drug_b = normalize_medication(drug_b_raw) or drug_b_raw.lower().strip()

    # Step 2: query all sources
    label_text = get_label_interactions(drug_a)
    adverse_count = get_adverse_event_count(drug_a, drug_b)
    pubchem_a = get_pubchem_data(drug_a)
    pubchem_b = get_pubchem_data(drug_b)
    pubmed_text = get_pubmed_abstracts(drug_a, drug_b)

    # Step 3: grade evidence
    if not has_sufficient_data(label_text, adverse_count, pubchem_a, pubchem_b, pubmed_text):
        return {
            'output': (
                'I was unable to find reliable data on this specific drug combination. '
                'Please consult your pharmacist or doctor.'
            ),
            'drug_a': drug_a, 'drug_b': drug_b,
            'sources': [], 'refused': True
        }

    # Step 4: build context and call Granite
    context = format_tool_results(drug_a, drug_b, label_text, adverse_count, pubchem_a, pubchem_b, pubmed_text)
    prompt = f'{context}\n\nPlease explain this interaction in plain English.'

    try:
        output_parts = replicate.run(
            MODEL,
            input={
                'messages': [
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 500
            }
        )
        raw = ''.join(output_parts)
        response = json.loads(raw)['choices'][0]['message']['content']
    except Exception:
        return {
            'output': 'An error occurred while generating the report. Please try again.',
            'drug_a': drug_a, 'drug_b': drug_b,
            'sources': [], 'refused': True
        }

    sources = []
    if label_text: sources.append('FDA drug label')
    if adverse_count > 0: sources.append(f'FDA FAERS ({adverse_count:,} reports)')
    if pubchem_a or pubchem_b: sources.append('PubChem')
    if pubmed_text: sources.append('PubMed')

    return {
        'output': response,
        'drug_a': drug_a, 'drug_b': drug_b,
        'sources': sources, 'refused': False
    }

def run_multi(drugs: list[str]) -> list[dict]:
    if len(drugs) < 2:
        return []
    return [run(a, b) for a, b in combinations(drugs, 2)]