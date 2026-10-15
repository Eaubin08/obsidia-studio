"""Studio-owned read-only inference adapter. No Monde UI, no CSSA, no writes to Obsidia."""
import json
import os
import urllib.error
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:8080/v1"
ALLOWED_HOSTS = ("127.0.0.1", "localhost", "[::1]")


class InferenceError(RuntimeError):
    pass


def config():
    # Settings belong to this repo; user can override via environment.
    return {
        "provider": os.getenv("OBSIDIA_STUDIO_AI_PROVIDER", "openai_compatible"),
        "base_url": os.getenv("OBSIDIA_STUDIO_AI_URL", DEFAULT_BASE).rstrip("/"),
        "model": os.getenv("OBSIDIA_STUDIO_AI_MODEL", "local"),
    }


def _endpoint(cfg):
    from urllib.parse import urlparse
    parsed = urlparse(cfg["base_url"])
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1") or parsed.username or parsed.password:
        raise InferenceError("Seuls les services HTTP locaux (localhost/127.0.0.1) sont autorisés.")
    if not parsed.path.endswith("/v1"):
        raise InferenceError("L'URL doit désigner la racine /v1 d'un serveur compatible OpenAI.")
    return cfg["base_url"] + "/chat/completions"


def generate(prompt, timeout=600):
    cfg = config()
    if cfg["provider"] != "openai_compatible":
        raise InferenceError("Fournisseur IA inconnu ; seul openai_compatible est activé.")
    url = _endpoint(cfg)
    body = json.dumps({
        "model": cfg["model"], "messages": [
            {"role": "system", "content": "Tu rédiges des PROPOSITIONS. Aucun accès aux fichiers, aucun outil, aucune publication. N'invente pas de faits ; marque {{placeholder}} les preuves manquantes."},
            {"role": "user", "content": prompt}
        ], "temperature": 0.5, "stream": False
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            parsed = json.loads(response.read(5_000_000).decode("utf-8"))
        content = parsed["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise InferenceError("Réponse IA vide.")
        return content
    except (OSError, ValueError, KeyError, IndexError, TypeError, urllib.error.URLError) as exc:
        raise InferenceError("Stack IA locale indisponible ou réponse incompatible : " + str(exc)[:240]) from exc


def probe(timeout=2):
    """Read-only model endpoint discovery; never generates text or launches a process."""
    cfg = config()
    try:
        endpoint = _endpoint(cfg)
        url = endpoint.removesuffix("/chat/completions") + "/models"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read(100_000).decode("utf-8"))
        models = [str(m.get("id", "")) for m in payload.get("data", []) if isinstance(m, dict)]
        return {"reachable": True, "models": models[:30], "message": "Serveur local joignable."}
    except (InferenceError, OSError, ValueError, TypeError, urllib.error.URLError) as exc:
        return {"reachable": False, "models": [], "message": str(exc)[:200]}


def status():
    cfg = config()
    try:
        url = _endpoint(cfg)
        # Status doesn't generate content or spend tokens.
        return {"configured": True, "provider": cfg["provider"], "model": cfg["model"],
                "endpoint": url, "ready": False, "note": "Configuration valide ; disponibilité à vérifier par un test explicite."}
    except InferenceError as exc:
        return {"configured": False, "provider": cfg["provider"], "model": cfg["model"],
                "ready": False, "note": str(exc)}
