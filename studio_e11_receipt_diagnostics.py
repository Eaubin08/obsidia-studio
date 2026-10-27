"""Bounded receipt observations only. No inference, authority, I/O or producer import."""
UNKNOWN = "UNKNOWN"
MAX_COUNT = 65_535
OMISSION_CATEGORIES = frozenset({"irrelevant_to_query", "visibility_hide", "ENTRY_LIMIT", "PACKET_SIZE_LIMIT", UNKNOWN})
B7_CATEGORIES = frozenset({"COREFERENCE", "SOURCE_SCOPE", "CONDITIONAL_ATTACHMENT", "TEMPORAL_REFERENCE",
    "DEIXIS", "ENTITY_IDENTITY", "CONTRADICTION", "UNKNOWN_TERM_OR_PREDICATE", "DOMAIN_SPECIFIC_AMBIGUITY",
    "WORLD_OR_PHYSICAL_REFERENCE", "OTHER_EXPLICIT_UNRESOLVED", UNKNOWN})
CLOSURE_CATEGORIES = frozenset({"OPEN", "CLOSED", "MIXED", UNKNOWN})
CLOSURE_REASON_CATEGORIES = frozenset({"NO_PREDICATE_UNIT", "FRAME_MISSING", "FRAME_AMBIGUITY",
    "FRAME_CONTRADICTION", "FRAME_UNRESOLVED_REFERENCE", "FRAME_OBLIQUE_ROLE_UNRESOLVED",
    "EVENT_REFERENCE", "META_TARGET", "INDEX_CONFLICT", UNKNOWN})
DEGRADATION_CATEGORIES = frozenset({"RECEIPT_DEGRADED", "COMPONENT_UNAVAILABLE", "COMPONENT_ERROR",
    "UNKNOWN_COMPONENT_STATUS", "PUBLIC_ERRORS_PRESENT", "NPL_UNAVAILABLE", "LYAPUNOV_UNAVAILABLE", UNKNOWN})
SURFACES = ("SENS", "B6", "B7", "E11", "NPL", "LYAPUNOV", "M41")
AVAILABILITY = frozenset({"PRESENT", "NOT_PRESENT", "UNAVAILABLE", "ERROR", "SKIPPED_BY_POLICY", UNKNOWN})
C1_STAGES = frozenset({"SEMANTIC_QUERY", "INTENT", "MICRO_CORE", "REVERSE_OS", "TREE_34D_INPUT",
    "SIGMA", "TREE_CANONICAL", "READONLY_PC_CONTEXT", "CONTEXT_PACKET_V2", "W1_RUNTIME_JOIN",
    "W2_X108_ADMISSION", "W3_BRODY", "W4_MEMORY_RETRIEVAL", "W4B_LOCAL_MODEL_EVIDENCE",
    "W5_TREE_BRIDGE", "W6B_SIGMA_BRIDGE", "DATA_PURITY_AGENT"})


def _obj(value):
    return value if type(value) is dict else {}


def _list(value):
    return value if type(value) is list and len(value) <= MAX_COUNT else None


def _known(value, allowed):
    return value if type(value) is str and value in allowed else UNKNOWN


def _categories(value, allowed):
    values = _list(value)
    return sorted({_known(v, allowed) for v in values}) if values is not None else [UNKNOWN]


def sanitize_receipt_diagnostics(result):
    """Shared API/client/journal allowlist. Missing fields stay UNKNOWN, never guessed."""
    result = _obj(result)
    clean = {}
    for field in ("b6_omission_count", "b7_request_count"):
        value = result.get(field)
        clean[field] = value if type(value) is int and 0 <= value <= MAX_COUNT else UNKNOWN
    for field, allowed in (("b6_omission_categories", OMISSION_CATEGORIES),
                           ("sens_closure_reason_categories", CLOSURE_REASON_CATEGORIES),
                           ("b7_request_categories", B7_CATEGORIES),
                           ("c1_degradation_reasons", DEGRADATION_CATEGORIES)):
        clean[field] = _categories(result.get(field), allowed)
    clean["sens_closure_category"] = _known(result.get("sens_closure_category"), CLOSURE_CATEGORIES)
    surfaces = _obj(result.get("cognitive_surface_availability"))
    clean["cognitive_surface_availability"] = {name: _known(surfaces.get(name), AVAILABILITY) for name in SURFACES}
    return clean


def _component_status(value):
    if type(value) is not str:
        return UNKNOWN
    # Match the contract status token, not arbitrary prefixes or free-form suffixes.
    parts = value.split(":", 2)
    token = parts[0]
    if token in C1_STAGES and len(parts) > 1 and parts[1] == "DEGRADED":
        return "ERROR"
    if token in {"OK", "READY"}:
        return "PRESENT"
    if token in {"SKIPPED_NOT_AVAILABLE", "UNAVAILABLE"}:
        return "UNAVAILABLE"
    if token in {"ERROR", "DEGRADED"}:
        return "ERROR"
    if token in {"SKIPPED_BY_PATH_POLICY", "SKIPPED_OPTIONAL_NOT_PROVIDED"}:
        return "SKIPPED_BY_POLICY"
    return UNKNOWN


def _closure_reason(value):
    if value == "no_predicate_unit":
        return "NO_PREDICATE_UNIT"
    if type(value) is str:
        prefixes = {"frame:missing:": "FRAME_MISSING", "frame:ambiguity:": "FRAME_AMBIGUITY",
            "frame:contradiction:": "FRAME_CONTRADICTION", "frame:unresolved_reference:": "FRAME_UNRESOLVED_REFERENCE",
            "frame:oblique_role_unresolved:": "FRAME_OBLIQUE_ROLE_UNRESOLVED",
            "event_reference:": "EVENT_REFERENCE", "meta_target:": "META_TARGET", "index_conflict:": "INDEX_CONFLICT"}
        for prefix, category in prefixes.items():
            if value.startswith(prefix):
                return category
    return UNKNOWN


def extract_receipt_diagnostics(receipt):
    """Observe only an accepted public receipt. Do not call this to reconstruct a refusal.

    PRESENT means a surface is exposed, not executed, true or semantically validated.
    Explicit empty lists mean zero; absent/malformed/over-bound lists mean UNKNOWN.
    """
    receipt = _obj(receipt)
    e11 = _obj(receipt.get("cognition_shadow_memory"))
    packet = _obj(e11.get("context_packet"))
    omissions = _list(packet.get("omitted"))
    requests = _list(e11.get("resolution_requests"))
    result = {
        "b6_omission_count": len(omissions) if omissions is not None else UNKNOWN,
        "b6_omission_categories": [_obj(v).get("reason") for v in omissions] if omissions is not None else None,
        "b7_request_count": len(requests) if requests is not None else UNKNOWN,
        "b7_request_categories": [_obj(v).get("unresolved_kind") for v in requests] if requests is not None else None,
    }
    surfaces = {name: UNKNOWN for name in SURFACES}
    if type(receipt.get("cognition_shadow_memory")) is dict:
        surfaces["E11"] = "PRESENT" if e11 else "NOT_PRESENT"
    if type(e11.get("context_packet")) is dict:
        surfaces["B6"] = "PRESENT" if packet else "NOT_PRESENT"
    if requests is not None:
        surfaces["B7"] = "PRESENT"  # availability of the request surface, including an empty list
    if "world_hypothesis_snapshot" in receipt:
        hypothesis = receipt["world_hypothesis_snapshot"]
        if hypothesis is None or type(hypothesis) is dict:
            surfaces["M41"] = "PRESENT" if hypothesis else "NOT_PRESENT"

    entries = _list(e11.get("state_entries"))
    frames = [v for v in entries if type(v) is dict and v.get("state_type") == "SENS_FRAME"] if entries is not None else []
    closures = [_obj(_obj(v.get("payload")).get("semantic_closure")) for v in frames]
    categories = {"CLOSED" if c.get("closed") is True else "OPEN" if c.get("closed") is False else UNKNOWN for c in closures}
    result["sens_closure_category"] = (UNKNOWN if not categories or UNKNOWN in categories else
                                       next(iter(categories)) if len(categories) == 1 else "MIXED")
    reason_categories = []
    for closure in closures:
        reasons = _list(closure.get("reasons"))
        if reasons is None:
            reason_categories.append(UNKNOWN)
        elif len(reason_categories) + len(reasons) > MAX_COUNT:
            reason_categories = [UNKNOWN]
            break
        else:
            reason_categories.extend(_closure_reason(v) for v in reasons)
    result["sens_closure_reason_categories"] = reason_categories if closures else None
    if entries is not None and any(_obj(v).get("state_type") == "SENS_FRAME_ERROR" for v in entries):
        surfaces["SENS"] = "ERROR"
    elif frames:
        surfaces["SENS"] = "PRESENT"
    elif entries == []:
        surfaces["SENS"] = "NOT_PRESENT"

    components = _obj(receipt.get("components"))
    for name in ("NPL", "LYAPUNOV"):
        surfaces[name] = _component_status(components.get(name))
    degradation = []
    if receipt.get("completeness") == "DEGRADED":
        degradation.append("RECEIPT_DEGRADED")
    elif receipt.get("completeness") != "COMPLETE":
        degradation.append(UNKNOWN)
    if not components or len(components) > MAX_COUNT:
        degradation.append(UNKNOWN)
    else:
        for value in components.values():
            status = _component_status(value)
            if status == "UNAVAILABLE":
                degradation.append("COMPONENT_UNAVAILABLE")
            elif status == "ERROR":
                degradation.append("COMPONENT_ERROR")
            elif status == UNKNOWN:
                degradation.append("UNKNOWN_COMPONENT_STATUS")
        for name in ("NPL", "LYAPUNOV"):
            if surfaces[name] == "UNAVAILABLE":
                degradation.append(name + "_UNAVAILABLE")
    errors = _list(receipt.get("errors"))
    if errors is None:
        degradation.append(UNKNOWN)
    elif errors:
        degradation.append("PUBLIC_ERRORS_PRESENT")
    result["c1_degradation_reasons"] = degradation
    result["cognitive_surface_availability"] = surfaces
    return sanitize_receipt_diagnostics(result)
