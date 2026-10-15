"""Adaptateur Studio vers l'API cognitive Obsidia (sans interface Monde/CSSA).

Brody reçoit les requêtes en premier. Le routeur interne Obsidia décide si
une preuve Qwen est utile. Studio ne contacte jamais Qwen directement.
"""
import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlparse

DEFAULT_BASE = "http://127.0.0.1:8000"
DEFAULT_ROUTE = "/api/brody/chat"


class InferenceError(RuntimeError):
    pass


def config():
    return {
        "provider": "obsidia_brody",
        "base_url": os.getenv("OBSIDIA_STUDIO_BRODY_URL", DEFAULT_BASE).rstrip("/"),
        "model": "OBSIDIA_ROUTED",
    }


def _endpoint(cfg):
    parsed = urlparse(cfg["base_url"])
    if (parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ("", "/")):
        raise InferenceError("L'API cognitive doit être une adresse HTTP locale sans chemin.")
    return cfg["base_url"] + DEFAULT_ROUTE


def _call(payload, timeout):
    req = urllib.request.Request(
        _endpoint(config()), data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read(5_000_000).decode("utf-8"))
    except (OSError, ValueError, TypeError, urllib.error.URLError) as exc:
        raise InferenceError("API Brody indisponible ou réponse invalide : " + str(exc)[:240]) from exc


def _ingress_call(prompt, timeout):
    """Opt-in governed ingress. No direct Qwen access from Studio."""
    if os.getenv("OBSIDIA_STUDIO_USE_INGRESS") != "1":
        return None
    if os.getenv("OBSIDIA_STUDIO_ENABLE_INGRESS") != "1":
        raise InferenceError("Ingress Studio non autorisé : OBSIDIA_STUDIO_ENABLE_INGRESS=1 requis.")
    payload = {
        "text": prompt,
        "session_id": "obsidia-studio-editorial",
        "allow_local_model": os.getenv("OBSIDIA_STUDIO_ENABLE_LOCAL_MODEL") == "1",
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8110/api/cognitive/ingress",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read(5_000_000).decode("utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise InferenceError("Ingress local indisponible : " + str(exc)[:200]) from exc


def generate(prompt, timeout=600):
    """Lecture/proposition cognitive uniquement ; aucune autorité d'action Studio."""
    payload = {
        "message": prompt, "language": "fr",
        "session_id": "obsidia-studio-editorial",
        # Le runtime Brody observé indique DISABLED_BY_POLICY lorsque True.
        # Ne pas promettre ni forcer un recours à Qwen depuis Studio.
        "allow_provider": False,
    }
    result = _ingress_call(prompt, timeout) if os.getenv("OBSIDIA_STUDIO_USE_INGRESS") == "1" else _call(payload, timeout)
    if not isinstance(result, dict):
        raise InferenceError("Réponse Brody non structurée.")
    if result.get("emits_act") is True or result.get("kernel_mutation") is True:
        raise InferenceError("Enveloppe Brody non conforme au contrat readonly.")
    # The governed ingress returns plain final_response, not Brody's <POST>.
    # Promote it to a DRAFT only with observed, applied local-model evidence;
    # a router ALLOW alone, or a readable fallback, must never suffice.
    if os.getenv("OBSIDIA_STUDIO_USE_INGRESS") == "1":
        route = result.get("route_decision") or {}
        stage = result.get("local_model_stage") or {}
        guarded = (
            result.get("status") == "READY_READONLY"
            and result.get("readonly") is True
            and result.get("advisory_only") is not False
            and result.get("decision_authority") == "KX108_ONLY"
            and result.get("allowed_to_act") is not True
            and result.get("memory_write") is not True
            and result.get("emits_act") is not True
            and result.get("kernel_mutation") is not True
            and route.get("router_status") == "ROUTER_OK"
            and route.get("fail_closed_hold") is False
            and route.get("gate_verdict") == "ALLOW"
            and stage.get("status") == "EVIDENCE_READY"
            and stage.get("eligible") is True
            and stage.get("attempted") is True
            and stage.get("model_call_used") is True
            and stage.get("evidence_applied") is True
            and stage.get("tokens_remote") == 0
        )
        draft = result.get("final_response")
        if not guarded or not isinstance(draft, str) or not draft.strip():
            details = ("route=" + str(route.get("router_status")) + "/" + str(route.get("gate_verdict"))
                       + ", model=" + str(stage.get("status"))
                       + ", applied=" + str(stage.get("evidence_applied"))
                       + ", readonly=" + str(result.get("readonly"))
                       + ", advisory=" + str(result.get("advisory_only"))
                       + ", status=" + str(result.get("status"))
                       + ", route_reason=" + str(route.get("reason", ""))[:140]
                       + ", brody_status=" + str((result.get("brody_sufficiency") or {}).get("status"))
                       + ", brody_next=" + str((result.get("brody_sufficiency") or {}).get("next_stage"))
                       + ", brody_reason=" + str((result.get("brody_sufficiency") or {}).get("reason"))[:120]
                       + ", model_eligible=" + str(stage.get("eligible"))
                       + ", model_enabled=" + str(stage.get("enabled_by_caller")))
            raise InferenceError("Ingress sans artefact éditorial vérifié : aucun brouillon. " + details)
        # Text is a candidate requiring editorial/factual human review.
        # Do not manufacture hooks or evidence claims not returned by cognition.
        return "<POST>\\n" + draft.strip() + "\\n</POST>"

    # Les sorties Brody peuvent diverger : le final_answer peut être un
    # fallback identitaire alors que response_md exprime une limite épistémique.
    # On accepte un artefact éditorial UNIQUEMENT s'il est présent explicitement.
    import re
    for field in ("response", "final_answer", "response_md"):
        value = result.get(field)
        if isinstance(value, str) and re.search(r"<POST>(.+?)</POST>", value, re.I | re.S):
            return value
    sources = []
    for key in ("final_answer_source", "response_source", "source", "engine_status"):
        value = result.get(key)
        if isinstance(value, str) and value:
            sources.append(key + "=" + value[:80])
    summary = "; ".join(sources) or "source_non_renseignée"
    raise InferenceError(
        "Brody a répondu sans artefact éditorial <POST>. "
        "Aucun brouillon produit. Diagnostic : " + summary
    )


def probe(timeout=2):
    """Probe HTTP de disponibilité, sans génération ni appel de Qwen."""
    try:
        endpoint = _endpoint(config())
        from urllib.parse import urlsplit
        root = urlsplit(endpoint)
        req = urllib.request.Request(root.scheme + "://" + root.netloc + "/openapi.json", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            doc = json.loads(response.read(1_000_000).decode("utf-8"))
        exists = DEFAULT_ROUTE in doc.get("paths", {})
        return {"reachable": True, "brody_route_declared": exists,
                "message": "API locale joignable." if exists else "API joignable, route Brody non déclarée."}
    except (OSError, ValueError, TypeError, urllib.error.URLError, InferenceError) as exc:
        return {"reachable": False, "brody_route_declared": False, "message": str(exc)[:200]}


def status():
    cfg = config()
    try:
        endpoint = _endpoint(cfg)
        return {"configured": True, "provider": cfg["provider"], "model": cfg["model"],
                "endpoint": endpoint, "ready": False,
                "note": "Contrat Brody configuré ; vérifier disponibilité et génération de bout en bout."}
    except InferenceError as exc:
        return {"configured": False, "provider": cfg["provider"], "model": cfg["model"],
                "ready": False, "note": str(exc)}
