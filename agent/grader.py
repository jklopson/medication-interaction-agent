# agent/grader.py

def has_sufficient_data(label_text, adverse_count, pubchem_a, pubchem_b, pubmed_text) -> bool:
    """
    Returns True if any source has usable data.
    Granite is never called if this returns False.

    Purpose of this step of the agent pipeline is to ensure no model hallucinations.
    If no real data is found, the user should be notified of this, not given false info
    """
    has_label = label_text is not None and len(label_text.strip()) > 50
    has_events = adverse_count > 100
    has_pubchem = (pubchem_a is not None and len(pubchem_a.strip()) > 50) or \
                  (pubchem_b is not None and len(pubchem_b.strip()) > 50)
    has_pubmed = pubmed_text is not None and len(pubmed_text.strip()) > 50
    return has_label or has_events or has_pubchem or has_pubmed