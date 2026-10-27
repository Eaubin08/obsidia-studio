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


# LOT 1 is independent from generate(), native editorial mode and governed ingress.
# Import only Studio contracts; no producer module, retrieval or model is called here.
class E11NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class E11Deadline:
    """Bound the entire HTTP operation, including a peer slowly streaming headers/body."""
    def __init__(self, seconds=30):
        import threading
        self.expired = threading.Event()
        self.connections = []
        self.sockets = []
        self.timer = threading.Timer(seconds, self.expire)
        self.timer.daemon = True

    def expire(self):
        import socket
        self.expired.set()
        # HTTPConnection can detach/close its socket after headers while HTTPResponse
        # still owns a readable makefile. Keep that socket for deadline shutdown too.
        for sock in tuple(self.sockets):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    def handler(self):
        import http.client
        deadline = self

        class Connection(http.client.HTTPConnection):
            def connect(self):
                super().connect()
                deadline.sockets.append(self.sock)
                if deadline.expired.is_set():
                    self.close()
                    raise TimeoutError()

        class Handler(urllib.request.HTTPHandler):
            def http_open(self, req):
                def factory(*args, **kwargs):
                    connection = Connection(*args, **kwargs)
                    deadline.connections.append(connection)
                    return connection
                return self.do_open(factory, req)
        return Handler()


def verify_e11_service(base_url):
    """Check the pinned local deployment; no expiry, PID or human-review gate."""
    from studio_e11_deployment import verify_checkpoint
    return verify_checkpoint(base_url)


def run_e11_experiment(text):
    """One opt-in, authenticated Brody call; no retry, fallback, producer import or post save."""
    import time
    import uuid
    import http.client
    from studio_e11_contract import (BASELINE_CHECKPOINT, PREVIOUS_CHECKPOINT, CHECKPOINT, MAX_RESPONSE_BYTES, ContractError, consume_envelope,
                                     failure_result, parse_envelope)
    from studio_experiment_journal import record_experiment
    experiment_id = str(uuid.uuid4())
    if os.getenv("OBSIDIA_STUDIO_ENABLE_E11_LOT1") != "1":
        return failure_result(experiment_id, "DISABLED")
    start = time.monotonic()
    response_bytes = 0
    deadline = None
    provenance = {"repository": "Eaubin08/obsidia-x108-proofs",
        "branch": "feat/jarvis-advanced-obsidia-integration-v0", "baseline_checkpoint": BASELINE_CHECKPOINT,
        "previous_configured_checkpoint": PREVIOUS_CHECKPOINT, "configured_checkpoint": CHECKPOINT,
        "service_verification": {"status": "UNVERIFIED"}}
    try:
        if type(text) is not str or not text.strip() or len(text) > 4096:
            raise ContractError("INVALID_INPUT")
        try:
            base = config()["base_url"]
            endpoint = _endpoint({"base_url": base})
            # Force validation of malformed/out-of-range ports before making a request.
            port = urlparse(endpoint).port
            if port is not None and not 1 <= port <= 65535:
                raise ValueError("port")
        except (InferenceError, ValueError, TypeError):
            raise ContractError("ENDPOINT_INVALID") from None
        key = os.getenv("OBSIDIA_STUDIO_API_KEY", "")
        if not key.strip() or "\r" in key or "\n" in key:
            raise ContractError("AUTH_REQUIRED")
        verification = verify_e11_service(base)
        if verification is None:
            raise ContractError("HOLD_ACTIVATION")
        provenance["service_verification"] = verification
        payload = {"message": text, "language": "fr", "session_id": experiment_id,
            "allow_provider": False, "allow_local_model": False,
            "allow_memory_candidate": False, "allow_manual_apply": False,
            "compact": False, "debug": False, "debug_full": False}
        request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-API-Key": key}, method="POST")
        # Disable environment proxies as well as redirects: credentials stay on loopback.
        deadline = E11Deadline()
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), E11NoRedirect(), deadline.handler())
        deadline.timer.start()
        try:
            with opener.open(request, timeout=30) as response:
                if response.getcode() != 200:
                    raise ContractError("HTTP_ERROR")
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                response_bytes = len(raw)
        finally:
            deadline.timer.cancel()
        if deadline.expired.is_set() or time.monotonic() - start > 30:
            raise ContractError("TIMEOUT")
        result = consume_envelope(parse_envelope(raw), experiment_id=experiment_id, provenance=provenance)
    except ContractError as exc:
        result = failure_result(experiment_id, exc.code, unavailable=exc.code == "TIMEOUT", provenance=provenance)
    except urllib.error.HTTPError as exc:
        # A generic 503 does not prove an authentication misconfiguration.
        # Do not inspect/log its potentially sensitive body to infer a cause.
        code = ("REDIRECT_REFUSED" if 300 <= exc.code < 400 else "AUTH_REJECTED" if exc.code in (401, 403)
                else "SERVICE_UNAVAILABLE" if exc.code == 503 else "HTTP_ERROR")
        result = failure_result(experiment_id, code, unavailable=code != "REDIRECT_REFUSED", provenance=provenance)
        exc.close()
    except TimeoutError:
        result = failure_result(experiment_id, "TIMEOUT", unavailable=True, provenance=provenance)
    except urllib.error.URLError as exc:
        code = "TIMEOUT" if isinstance(exc.reason, TimeoutError) or (
            deadline is not None and deadline.expired.is_set()) else "SERVICE_UNAVAILABLE"
        result = failure_result(experiment_id, code, unavailable=True, provenance=provenance)
    except (OSError, ValueError, TypeError, http.client.HTTPException):
        code = "TIMEOUT" if deadline is not None and deadline.expired.is_set() else "SERVICE_UNAVAILABLE"
        result = failure_result(experiment_id, code, unavailable=True, provenance=provenance)
    try:
        record_experiment(result, elapsed_ms=(time.monotonic() - start) * 1000, response_bytes=response_bytes)
    except (OSError, ValueError, TypeError, KeyError):
        # Withhold all context if the metadata journal cannot be recorded. No second log attempt.
        return failure_result(experiment_id, "JOURNAL_UNAVAILABLE", provenance=provenance)
    return result


def _endpoint(cfg):
    parsed = urlparse(cfg["base_url"])
    if (parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ("", "/")):
        raise InferenceError("L'API cognitive doit être une adresse HTTP locale sans chemin.")
    return cfg["base_url"] + DEFAULT_ROUTE


def _call(payload, timeout):
    from studio_e11_contract import ContractError, parse_envelope
    # Same credential as LOT 1; never send it through proxies or redirects.
    key = os.getenv("OBSIDIA_STUDIO_API_KEY", "")
    if not key.strip() or "\r" in key or "\n" in key:
        raise InferenceError("AUTH_REQUIRED: clé Brody Studio absente ou invalide.")
    req = urllib.request.Request(
        _endpoint(config()), data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-API-Key": key}, method="POST")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), E11NoRedirect())
    try:
        with opener.open(req, timeout=timeout) as response:
            raw = response.read(5_000_001)
            if len(raw) > 5_000_000:
                raise InferenceError("BRODY_RESPONSE_TOO_LARGE")
            return parse_envelope(raw)
    except urllib.error.HTTPError as exc:
        status = exc.code
        exc.close()
        raise InferenceError("BRODY_HTTP_" + str(status)) from None
    except (OSError, ValueError, TypeError, urllib.error.URLError, ContractError):
        # Exception messages and server bodies can contain credentials.
        raise InferenceError("BRODY_NETWORK_OR_RESPONSE_ERROR") from None


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
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), E11NoRedirect())
        with opener.open(req, timeout=timeout) as response:
            return json.loads(response.read(5_000_000).decode("utf-8"))
    except (OSError, ValueError, TypeError):
        raise InferenceError("INGRESS_NETWORK_OR_RESPONSE_ERROR") from None




def _editorial_provenance(result):
    """Report observed source, never infer a Brody synthesis from a Qwen join."""
    suff = result.get("brody_sufficiency") or {}
    stage = result.get("local_model_stage") or {}
    final = result.get("final_answer_snapshot") or {}
    if not isinstance(final, dict):
        final = {}
    qwen_applied = stage.get("evidence_applied") is True
    if qwen_applied:
        # The current final adapter can select projection_content unchanged.
        # A cognitive join is NOT evidence of a new Brody composition.
        source = "GOVERNED_MODEL_PROJECTION"
    elif suff.get("status") == "BRODY_SUFFICIENT":
        source = "BRODY_NATIVE"
    else:
        source = "UNKNOWN"
    return {
        "source": source,
        "brody_sufficient": suff.get("status") == "BRODY_SUFFICIENT",
        "qwen_evidence_applied": qwen_applied,
        "brody_post_model_synthesis_proven": False,
        "human_approval_required": True,
        "publication_permitted": False,
        "final_adapter_status": final.get("v1_4_12a_status_tag"),
        "projection_selected": final.get("governed_model_projection_selected"),
    }

def _native_editorial_request(subject):
    """Request actual authored content from Brody's existing chat interface.

    Used on the native Brody endpoint; the governed ingress receives the same
    explicit editorial intent from editorial_intent, not a bare subject.
    """
    if not isinstance(subject, str) or not subject.strip():
        raise InferenceError("Sujet éditorial vide.")
    text = subject.strip()
    # Preserve an explicit writing brief verbatim. Bare subjects acquire only
    # the editorial task; no router entitlement or semantic content is invented.
    if text.casefold().startswith(("rédige ", "redige ", "écris ", "ecris ")):
        return text
    return "Rédige une publication LinkedIn expliquant " + text



def generate(prompt, timeout=600, *, return_receipt=False, use_ingress=None, editorial_version="V1", internal_observation_id=None):
    """Lecture/proposition cognitive uniquement ; aucune autorité d'action Studio."""
    if type(editorial_version) is not str or editorial_version not in {"V1", "V2"}:
        raise InferenceError("EDITORIAL_VERSION_INVALID")
    payload = {
        "message": _native_editorial_request(prompt), "language": "fr",
        "session_id": "obsidia-studio-editorial",
        # Le runtime Brody observé indique DISABLED_BY_POLICY lorsque True.
        # Ne pas promettre ni forcer un recours à Qwen depuis Studio.
        "allow_provider": False,
        "allow_local_model": False,
        "allow_memory_candidate": False,
        "allow_manual_apply": False,
    }
    ingress_selected = (os.getenv("OBSIDIA_STUDIO_USE_INGRESS") == "1") if use_ingress is None else (use_ingress is True)
    if internal_observation_id is not None:
        if ingress_selected:
            raise InferenceError("OBSERVATION_NATIVE_ENDPOINT_REQUIRED")
        try:
            from studio_internal_observation import reference_for
            reference_for(internal_observation_id, payload['message'], lambda **kw: kw)
        except (ValueError, OSError, TypeError, KeyError):
            raise InferenceError("INTERNAL_OBSERVATION_REFERENCE_INVALID") from None
        payload['internal_observation_id'] = internal_observation_id
    if editorial_version == "V2":
        if ingress_selected:
            raise InferenceError("V2_NATIVE_ENDPOINT_REQUIRED")
        payload["editorial_version"] = "V2"
    result = _ingress_call(prompt, timeout) if ingress_selected else _call(payload, timeout)
    if not isinstance(result, dict):
        raise InferenceError("Réponse Brody non structurée.")
    if result.get("emits_act") is True or result.get("kernel_mutation") is True:
        raise InferenceError("Enveloppe Brody non conforme au contrat readonly.")
    if (result.get("readonly") is not True or result.get("decision_authority") != "KX108_ONLY"
            or any(result.get(k) is True for k in ("allowed_to_act", "allowed_to_decide", "memory_write", "canonical_write", "x108_mutation"))
            or result.get("status") in ("HOLD", "BLOCK", "REFUSED", "DEFERRED")):
        raise InferenceError("GOVERNANCE_REFUSED: enveloppe éditoriale non conforme.")
    sufficiency = result.get("brody_sufficiency")
    if isinstance(sufficiency, dict) and (sufficiency.get("status") in
            {"HOLD", "BLOCK", "GOVERNANCE_BOUNDARY"} or sufficiency.get("contradictions") or sufficiency.get("risk_flags")):
        raise InferenceError("GOVERNANCE_BOUNDARY")
    # Native admission precedes the generic unresolved-symbol refusal: unknown
    # labels remain in the snapshot while dependent assertions stay blocked.
    if "editorial_artifact" in result or "editorial_route_status" in result:
        from studio_native_editorial import validate_native_artifact
        try:
            # Ingress has no attested public-native deployment at this port.
            if ingress_selected:
                raise ValueError("NATIVE_ENDPOINT_UNVERIFIED")
            artifact, provenance = validate_native_artifact(result, payload["message"], base_url=config()["base_url"], editorial_version=editorial_version,
                **({'internal_observation_id':internal_observation_id} if internal_observation_id is not None else {}))
        except (ValueError, TypeError, KeyError, OSError):
            raise InferenceError("BRODY_NATIVE_ARTIFACT_INVALID") from None
        return (artifact, provenance) if return_receipt else artifact
    for name in ("pre_reasoning_snapshot", "brody_sufficiency"):
        snapshot = result.get(name) or {}
        if not isinstance(snapshot, dict):
            raise InferenceError("BRODY_CONTRACT_INVALID")
        directive = snapshot.get("reasoning_directive") or {}
        qualification = snapshot.get("unknown_qualification") or {}
        if (not isinstance(directive, dict) or not isinstance(qualification, dict)
                or directive.get("resolution_required") is True or qualification.get("unresolved_unknowns")):
            raise InferenceError("BRODY_PRE_REASONING_RESOLUTION_REQUIRED")
    # Legacy B6, source labels, plain Ingress text and model projections are
    # insufficient evidence of native editorial authorship, even with <POST>.
    source = result.get("final_answer_source", result.get("source", "UNKNOWN"))
    if source not in {"TERMINAL_DIALOGUE_IDENTITY", "B6_ADVISORY_CONTEXT"}:
        source = "UNVERIFIED_OUTPUT"
    raise InferenceError("BRODY_AUTHOR_UNPROVEN: " + source)



def probe(timeout=2):
    """Probe HTTP de disponibilité, sans génération ni appel de Qwen."""
    try:
        endpoint = _endpoint(config())
        from urllib.parse import urlsplit
        root = urlsplit(endpoint)
        key = os.getenv("OBSIDIA_STUDIO_API_KEY", "")
        if not key.strip() or "\r" in key or "\n" in key:
            raise InferenceError("AUTH_REQUIRED")
        req = urllib.request.Request(root.scheme + "://" + root.netloc + "/openapi.json",
                                     headers={"X-API-Key": key}, method="GET")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), E11NoRedirect())
        with opener.open(req, timeout=timeout) as response:
            doc = json.loads(response.read(1_000_000).decode("utf-8"))
        exists = DEFAULT_ROUTE in doc.get("paths", {})
        return {"reachable": True, "brody_route_declared": exists,
                "message": "API locale joignable." if exists else "API joignable, route Brody non déclarée."}
    except (OSError, ValueError, TypeError, urllib.error.URLError, InferenceError) as exc:
        return {"reachable": False, "brody_route_declared": False, "message": "BRODY_PROBE_UNAVAILABLE_OR_AUTH_REQUIRED"}


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
