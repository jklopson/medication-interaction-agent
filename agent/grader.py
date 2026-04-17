# agent/grader.py

def has_sufficient_data(label_text: str | None, adverse_count: int) -> bool:
    """
    Returns True only if we have enough real FDA data to ground a response.
    Granite is never called if this returns False.

    Purpose of this step of the agent pipeline is to ensure no model hallucinations.
    If no real data is found, the user should be notified of this, not given false info
    """
    has_label = label_text is not None and len(label_text.strip()) > 50
    has_events = adverse_count > 100
    return has_label or has_events
