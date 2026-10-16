"""Studio editorial quality checks. Deterministic, no external state or model calls."""
import re


def assess(text, network="linkedin"):
    text = (text or "").strip()
    issues = []
    if not text:
        return {"ok": False, "issues": ["Texte vide"]}
    if re.search(r"sur (?:le reseau )?linkedin[, ]+(?:je partage|je souhaite partager)", text, re.I):
        issues.append("Accroche meta LinkedIn : commencer directement par l'idee.")
    if re.search(r"(?:l'ia|une ia|elle)\s+(?:ne doit jamais|ne devrait jamais)\s+(?:etre autorisee a |pouvoir )?executer", text, re.I):
        issues.append("Autorite erronee : l'execution est possible apres autorisation controlee.")
    if re.search(r"(?:l'ia|une ia)\s+doit\s+comprendre,?\s+proposer\s+et\s+autoriser", text, re.I):
        issues.append("Autorite erronee : KX108 decide, la proposition n'autorise rien.")
    if text.upper().startswith(("RESEAU :", "SUJET :")):
        issues.append("Prompt recopie dans le texte.")
    if "par herself" in text.lower():
        issues.append("Fragment non francais dans le texte.")
    if "kx108" in text.lower() and "consultatif" in text.lower():
        issues.append("Autorite erronee : KX108 ne doit pas etre presente comme consultatif.")
    # Repeated blocks are a known failure mode of small local models.
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    if re.search(r"(.{70,}?)\1", normalized):
        issues.append("Repetition d un meme passage dans le post.")
    if text.startswith(("# ", "## ", "### ", "\\\\### ")):
        issues.append("Balises Markdown dans l accroche.")
    if network == "linkedin":
        if len(text) < 400:
            issues.append("Post tres court : manque de developpement.")
        if len(text) > 3000:
            issues.append("Depasse 3000 caracteres.")
        if len([p for p in re.split(r"\n\s*\n", text) if p.strip()]) < 3:
            issues.append("Structure : separer accroche et paragraphes courts.")
    return {"ok": not issues, "issues": issues}
