"""Conservative display cleanup for governed editorial drafts.

Never invent, fact-check, or rewrite claims. Only remove recognizable
model chatter and literal newline escape sequences before human review.
"""
import re

_INTRO = re.compile(
    r"^(?:voici|je vous propose|je te propose)\s+(?:une\s+)?"
    r"(?:courte\s+)?(?:publication|proposition|version|texte|post)\b[^\n:]{0,200}:\s*",
    re.I,
)
_OUTRO = re.compile(
    r"\s+(?:cette publication|ce post|ce texte)\s+"
    r"(?:respecte|couvre|est adapté|est concis|est une proposition)\b.*$",
    re.I | re.S,
)


def clean_editorial_draft(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("draft must be a string")
    clean = text.strip()
    # Actual response may contain the two ASCII chars backslash + n.
    clean = clean.replace("\\r\\n", "\\n").replace("\\n", "\n")
    clean = clean.strip()
    intro = _INTRO.match(clean)
    if intro:
        body = clean[intro.end():].strip()
        # The wrapper must clearly delimit a quoted draft; otherwise
        # remove only the obvious introductory sentence.
        if body.startswith(('"', "«")):
            closer = '"' if body[0] == '"' else "»"
            end = body.rfind(closer)
            if end > 0 and (end == len(body) - 1 or _OUTRO.fullmatch(body[end + 1:])):
                clean = body[1:end].strip()
            else:
                clean = body
        else:
            clean = body
            clean = _OUTRO.sub("", clean).strip()
    # Model sometimes echoes the prompt constraint after the closing quote.
    # Strip only a known *standalone* instruction, not ordinary authored prose.
    clean = re.sub(
        r"\s+N[’']invente aucun fait ou chiffre\.?\s*$",
        "", clean, flags=re.I,
    ).strip()
    # A complete externally quoted post (possibly followed by an echoed
    # instruction) can be unwrapped without changing its actual words.
    if len(clean) >= 2 and (
        (clean.startswith('"') and clean.endswith('"'))
        or (clean.startswith("«") and clean.endswith("»"))
    ):
        clean = clean[1:-1].strip()
    return clean.strip()
