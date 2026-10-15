"""Studio-owned, explicitly selected editorial inference via a local Ollama API.

No external repository modification, no privileged actions, no publication,
no kernel decisions. This is NOT a retry after a governed HOLD.
"""
import json
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse


class EditorialEngineError(RuntimeError):
    pass


def _endpoint():
    raw = os.getenv("OBSIDIA_STUDIO_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    u = urlparse(raw)
    if (u.scheme != "http" or u.hostname not in ("localhost", "127.0.0.1", "::1")
            or u.username or u.password or u.query or u.fragment or u.path not in ("", "/")):
        raise EditorialEngineError("Le moteur editorial doit etre sur une URL HTTP locale sans chemin.")
    return raw + "/api/chat"


def generate_editorial(idea, *, network="LinkedIn", source_text="", timeout=120):
    """Return a proposed draft, with accurate Studio-owned model provenance."""
    idea = str(idea or "").strip()
    source_text = str(source_text or "").strip()
    model = os.getenv("OBSIDIA_STUDIO_OLLAMA_MODEL", "").strip()
    if not model:
        raise EditorialEngineError(
            "Modele local non configure : definissez OBSIDIA_STUDIO_OLLAMA_MODEL "
            "(modele disponible via Ollama)."
        )
    if not idea and not source_text:
        raise EditorialEngineError("Sujet ou texte source requis.")
    if len(idea) > 8000 or len(source_text) > 16000:
        raise EditorialEngineError("Entree editoriale trop longue.")
    system = (
        "Tu es le redacteur consultatif d'Obsidia Studio. Produis un VRAI "
        "brouillon de publication en francais pour le reseau demande. "
        "N'affirme aucune realisation, statistique, etude ou citation sans "
        "preuve presente dans le texte source fourni. Ne transforme pas "
        "une hypothese en resultat. Si un detail manque, reste general et "
        "nuance. Ne publie rien et ne demande aucune action externe. "
        "Renvoie uniquement le texte final de la publication, sans balises, "
        "sans meta-commentaires ni diagnostic interne."
    )
    user = "RESEAU : " + str(network) + "\nSUJET : " + idea
    if source_text:
        user += "\nTEXTE SOURCE UTILISATEUR (non verifie) :\n" + source_text
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {"temperature": 0.6, "num_predict": 650},
    }
    request = urllib.request.Request(
        _endpoint(),
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read(2_000_000).decode("utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise EditorialEngineError("Moteur local indisponible ou reponse invalide : " + str(exc)[:200]) from exc
    if not isinstance(data, dict) or data.get("model") != model:
        raise EditorialEngineError("Identite du modele non verifiable.")
    message = data.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise EditorialEngineError("Le moteur n'a pas produit de brouillon.")
    content = content.strip()
    if (content.startswith("Synthese readonly depuis source-pack")
            or content.startswith("PRE_REASONING_UNRESOLVED")
            or content.startswith("DOMAIN_RACCORD_READONLY")):
        raise EditorialEngineError("Diagnostic renvoye a la place d'un brouillon.")
    return {
        "text": content,
        "provenance": {
            "source": "STUDIO_LOCAL_OLLAMA",
            "model": model,
            "brody_post_model_synthesis_proven": False,
            "qwen_evidence_applied": False,
            "human_approval_required": True,
            "publication_permitted": False,
            "cognitive_gate": "NOT_CALLED",
        },
        "warning": "Brouillon genere par le modele local de Studio, non par Brody. Verifier faits et ton avant validation.",
    }
