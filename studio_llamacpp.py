"""Studio-only adapter for existing llama.cpp llama-server (OpenAI-compatible HTTP).

No changes to llama.cpp installation or any other repository.
Explicit opt-in. No fallback from governed HOLD.
"""
import json
import os
import urllib.request
from urllib.parse import urlparse

from studio_editorial_engine import EditorialEngineError


def _endpoint():
    raw = os.getenv("OBSIDIA_STUDIO_LLAMACPP_URL", "http://127.0.0.1:8080").rstrip("/")
    u = urlparse(raw)
    if (u.scheme != "http" or u.hostname not in ("localhost", "127.0.0.1", "::1")
            or u.username or u.password or u.query or u.fragment
            or u.path not in ("", "/")):
        raise EditorialEngineError("llama-server doit utiliser une adresse HTTP locale sans chemin.")
    return raw + "/v1/chat/completions"


def generate_llamacpp(idea, *, network="LinkedIn", source_text="", timeout=180):
    idea = str(idea or "").strip()
    source_text = str(source_text or "").strip()
    if not idea and not source_text:
        raise EditorialEngineError("Sujet ou texte source requis.")
    if len(idea) > 8000 or len(source_text) > 16000:
        raise EditorialEngineError("Entree editoriale trop longue.")
    model = os.getenv("OBSIDIA_STUDIO_LLAMACPP_MODEL", "local").strip() or "local"
    system = (
        "Tu es le redacteur d'Obsidia Studio. Ecris un post en francais avec "
        "une accroche directe sur sa premiere ligne, puis 2 a 4 courts "
        "paragraphes separes par des lignes vides. Evite le ton scolaire, "
        "les repetitions, les introductions comme 'Sur LinkedIn je partage', "
        "et les conclusions generiques. Pour une question de gouvernance IA, "
        "distingue comprendre, proposer, autoriser, executer et prouver ; "
        "KX108 est seul decisionnaire, Brody reste consultatif. Ne presente "
        "pas ces principes comme des resultats experimentalement prouves. "
        "N'invente aucun test, chiffre, citation, client ou realisation. "
        "Les faits du texte utilisateur sont non verifies. "
        "Reste descriptif sur le reste ; ne publie rien et n'effectue "
        "aucune action externe. Retourne seulement le brouillon."
    )
    prompt = "Redige une publication pour " + str(network) + " sur le theme suivant : " + idea
    if source_text:
        prompt += "\nTEXTE UTILISATEUR NON VERIFIE :\n" + source_text
    payload = {
        "model": model,
        "stream": False,
        "temperature": 0.6,
        "max_tokens": 650,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        _endpoint(), data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read(2_000_000).decode("utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise EditorialEngineError("llama-server indisponible ou reponse invalide : " + str(exc)[:200]) from exc
    choices = data.get("choices") if isinstance(data, dict) else None
    message = choices[0].get("message") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
    text = message.get("content") if isinstance(message, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise EditorialEngineError("llama-server n'a pas retourne de brouillon.")
    text = text.strip()
    if (text.lower().startswith("synthese readonly depuis source-pack")
            or text.startswith("DOMAIN_RACCORD_READONLY")
            or text.startswith("PRE_REASONING_UNRESOLVED")):
        raise EditorialEngineError("Diagnostic recu au lieu d'un post.")
    return {
        "text": text,
        "provenance": {
            "source": "STUDIO_LOCAL_LLAMACPP",
            "model": str(data.get("model") or model),
            "human_approval_required": True,
            "publication_permitted": False,
            "brody_post_model_synthesis_proven": False,
            "qwen_evidence_applied": False,
            "cognitive_gate": "NOT_CALLED",
        },
        "warning": "Brouillon genere par llama.cpp pour Studio, et non par Brody ; verification humaine requise.",
    }
