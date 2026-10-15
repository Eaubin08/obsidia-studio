"""Construct a bounded, readonly editorial request without lexical boilerplate.

The semantic router must evaluate the user's actual subject, not a string of
platform instructions that becomes a source of false semantic unknowns.
No governance verdict, model entitlement, or authority is set here.
"""
def explanatory_editorial_request(subject: str, network: str = "LinkedIn", source_text: str = "") -> str:
    subject = subject.strip()
    if not subject:
        raise ValueError("Sujet éditorial requis")
    # Preserve question meaning. Do not inject platform/style vocabulary into
    # the cognitive question: it previously created false semantic debt.
    if subject.endswith("?"):
        prompt = subject
    else:
        prompt = f"Pourquoi {subject.rstrip('.')} ?"
    # Sources are optional additional evidence only; they are not directives
    # to perform actions or claims that Brody has acquired knowledge.
    if source_text.strip():
        prompt += "\n\nContexte fourni :\n" + source_text.strip()[:6000]
    return prompt
