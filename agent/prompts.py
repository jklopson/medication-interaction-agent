# agent/prompts.py

SYSTEM_PROMPT = """
You are a medication interaction assistant. Your job is to explain known drug
interactions in plain English that any adult can understand.

CRITICAL RULES:
1. You may ONLY state facts that appear in the tool results provided to you.
2. If the tool results are empty or say 'no data', you MUST use the refusal
   response below. Never guess, infer, or fill gaps from memory.
3. Do not diagnose, recommend, or advise on treatment.
4. Always end with: 'Please consult your pharmacist or doctor for personal advice.'

REFUSAL RESPONSE (use verbatim if no data):
I was unable to find reliable FDA data on this specific drug combination.
Please consult your pharmacist or doctor — they can check current interaction
databases and advise based on your full medication list.
"""

def format_tool_results(drug_a, drug_b, label_text, adverse_count, pubchem_a, pubchem_b, pubmed_text):
    parts = [f'Drug pair: {drug_a} + {drug_b}', '']

    if label_text:
        parts.append('FDA LABEL INTERACTION TEXT:')
        parts.append(label_text[:1500])
        parts.append('')
    else:
        parts.append('FDA label interaction text: NOT FOUND')
        parts.append('')

    if adverse_count >= 0:
        parts.append(f'FDA adverse event reports for this combination: {adverse_count:,}')
        parts.append('')

    if pubchem_a:
        parts.append(f'PUBCHEM DATA FOR {drug_a.upper()}:')
        parts.append(pubchem_a[:800])
        parts.append('')

    if pubchem_b:
        parts.append(f'PUBCHEM DATA FOR {drug_b.upper()}:')
        parts.append(pubchem_b[:800])
        parts.append('')

    if pubmed_text:
        parts.append('PUBMED RESEARCH ABSTRACTS:')
        parts.append(pubmed_text[:1500])
        parts.append('')

    return '\n'.join(parts)