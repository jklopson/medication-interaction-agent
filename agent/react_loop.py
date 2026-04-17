# agent/react_loop.py
import replicate, os, json
from dotenv import load_dotenv
from tools.rxnorm import normalize_medication
from tools.openfda import get_label_interactions, get_adverse_event_count
from agent.prompts import SYSTEM_PROMPT, format_tool_results
from agent.grader import has_sufficient_data

load_dotenv()
MODEL = os.getenv('GRANITE_MODEL')

def run(drug_a_raw: str, drug_b_raw: str) -> dict:
    """
    Full agent run. Returns dict with keys:
      output (str), drug_a (str), drug_b (str), sources (list), refused (bool)
    """
    # Step 1: normalize names via RxNorm
    drug_a = normalize_medication(drug_a_raw) or drug_a_raw.lower().strip()
    drug_b = normalize_medication(drug_b_raw) or drug_b_raw.lower().strip()

    # Step 2: call both FDA tools
    label_text = get_label_interactions(drug_a)
    adverse_count = get_adverse_event_count(drug_a, drug_b)

    # Step 3: grade evidence (refuse if insufficient)
    if not has_sufficient_data(label_text, adverse_count):
        return {
            'output': (
                'I was unable to find reliable FDA data on this specific drug combination. '
                'Please consult your pharmacist or doctor.'
            ),
            'drug_a': drug_a, 'drug_b': drug_b,
            'sources': [], 'refused': True
        }

    # Step 4: build context and call Granite
    context = format_tool_results(drug_a, drug_b, label_text, adverse_count)
    prompt = f'{context}\n\nPlease explain this interaction in plain English.'

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

    sources = []
    if label_text: sources.append('FDA drug label')
    if adverse_count > 0: sources.append(f'FDA FAERS ({adverse_count:,} reports)')

    return {
        'output': response,
        'drug_a': drug_a, 'drug_b': drug_b,
        'sources': sources, 'refused': False
    }
