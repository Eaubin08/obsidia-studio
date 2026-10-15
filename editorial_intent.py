"""Studio text-only explanatory request construction for governed ingress.

This is a question to the cognitive system, not an authority override.
"""
def explanatory_editorial_request(subject: str, network: str = "LinkedIn", source_text: str = "") -> str:
    subject = subject.strip()
    if not subject:
        raise ValueError("Sujet éditorial requis")
    prompt = (
        f"Comment expliquer en français, pour un brouillon consultatif {network}, "
        f"le sujet suivant : {subject} ? "
        "Présenter uniquement les faits disponibles et leurs limites."
    )
    if source_text.strip():
        prompt += "\nTexte utilisateur pour contextualisation en lecture seule :\n" + source_text.strip()[:6000]
    return prompt
