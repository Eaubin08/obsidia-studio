"""Test Studio cognitive generation without the UI or post/image writes.

Run: python diagnose_generation.py --subject "Pourquoi une IA doit vérifier avant d'agir ?"
Does not change upstream authority classification, retry HOLD, or call Qwen directly.
"""
import argparse
import json
import os
import sys

import studio_ai


def intent_trace(value, prefix="", depth=0):
    """Only categorical decision metadata; no full user text or model output."""
    found = {}
    if depth > 5 or len(found) > 100:
        return found
    if isinstance(value, dict):
        for key, item in value.items():
            name = str(key)
            path = f"{prefix}.{name}" if prefix else name
            if any(token in name.lower() for token in (
                "intent", "request_type", "authority", "contradiction",
                "risk_flag", "reason_code", "boundary_violation",
            )):
                if isinstance(item, (str, int, float, bool)) or item is None:
                    found[path] = str(item)[:160]
                elif isinstance(item, list):
                    found[path] = [str(x)[:160] for x in item[:10]]
            if isinstance(item, dict):
                found.update(intent_trace(item, path, depth + 1))
    return found


def snapshot(result):
    route = result.get("route_decision") or {}
    suff = result.get("brody_sufficiency") or {}
    model = result.get("local_model_stage") or {}
    authority = result.get("authority_snapshot") or {}
    ir = result.get("ir_candidate") or {}
    return {
        "result_status": result.get("status"),
        "route_verdict": route.get("gate_verdict"),
        "router_status": route.get("router_status"),
        "authority_request_type": authority.get("request_type"),
        "ir_intent": ir.get("intent_type"),
        "brody_status": suff.get("status"),
        "brody_reason": suff.get("reason"),
        "contradictions": suff.get("contradictions"),
        "risk_flags": suff.get("risk_flags"),
        "model_status": model.get("status"),
        "model_applied": model.get("evidence_applied"),
        "final_answer_present": bool((result.get("final_response") or "").strip()),
        "readonly": result.get("readonly"),
        "emits_act": result.get("emits_act"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", default="Comment expliquer la gouvernance des IA ?")
    parser.add_argument("--timeout", type=int, default=120)
    opts = parser.parse_args(argv)
    print("MODE=READ_ONLY_DIAGNOSTIC")
    print("NO_POST_WRITE=TRUE")
    print("NO_QWEN_DIRECT=TRUE")
    if os.getenv("OBSIDIA_STUDIO_ENABLE_INGRESS") != "1":
        print("ERROR=OBSIDIA_STUDIO_ENABLE_INGRESS must be 1")
        return 2
    from editorial_intent import explanatory_editorial_request
    prompt = explanatory_editorial_request(opts.subject, network="LinkedIn")
    try:
        result = studio_ai._ingress_call(prompt, opts.timeout)
    except studio_ai.InferenceError as exc:
        print("ERROR=" + str(exc))
        return 2
    if not isinstance(result, dict):
        print("ERROR=NON_DICT")
        return 2
    details = snapshot(result)
    print(json.dumps(details, ensure_ascii=False, indent=2, default=str))
    if suff := result.get("brody_sufficiency"):
        # Surface structural reasons instead of treating a readable fallback
        # as a produced editorial artifact.
        allowed = ("status", "reason", "next_stage", "sufficient",
                   "semantic_resolution", "semantic_resolution_status",
                   "missing_fields", "missing_components", "requirements",
                   "output_contract_ok", "brody_boundary_ok",
                   "resolution_required", "pre_reasoning",
                   "evidence_needed", "requires_kx108_decision")
        print("=== BRODY_RESOLUTION_DETAILS ===")
        print(json.dumps({k: v for k, v in suff.items() if k in allowed},
                         ensure_ascii=False, indent=2, default=str))
    route_debug = result.get("route_decision") or {}
    print("=== ROUTE_IR_DETAILS ===")
    print(json.dumps({
        "gate_verdict": route_debug.get("gate_verdict"),
        "reason": route_debug.get("reason"),
        "ir": route_debug.get("ir"),
        "brody_stage_status": (result.get("brody_stage") or {}).get("status"),
        "llm_activation_status": (result.get("llm_activation") or {}).get("status"),
    }, ensure_ascii=False, indent=2, default=str))
    print("=== DECISION_METADATA_TRACE ===")
    trace = intent_trace({k: v for k, v in result.items() if k not in ("final_response", "surface_response", "final_answer_snapshot", "context_packet_v2")})
    print(json.dumps(trace, ensure_ascii=False, indent=2, default=str))
    suff = result.get("brody_sufficiency") or {}
    route = result.get("route_decision") or {}
    if suff.get("status") == "GOVERNANCE_BOUNDARY" or route.get("gate_verdict") in ("HOLD", "BLOCK"):
        print("VERDICT=UPSTREAM_GOVERNANCE_BOUNDARY_NOT_STUDIO_PARSER")
        return 3
    if route.get("gate_verdict") != "ALLOW":
        print("VERDICT=ROUTE_NOT_ALLOWED_" + str(route.get("gate_verdict")))
        return 5
    if suff.get("status") not in ("BRODY_SUFFICIENT", "BRODY_INSUFFICIENT"):
        print("VERDICT=BRODY_NOT_EDITORIAL_READY_" + str(suff.get("status")))
        return 6
    try:
        # Same contract as Studio, without posting or generating images.
        from unittest.mock import patch
        with patch.object(studio_ai, "_ingress_call", return_value=result):
            artifact, receipt = studio_ai.generate(prompt, return_receipt=True, use_ingress=True)
    except studio_ai.InferenceError:
        print("VERDICT=STUDIO_EDITORIAL_CONTRACT_REJECTED")
        return 7
    print("EDITORIAL_ARTIFACT_CHARS=" + str(len(artifact)))
    print("PROVENANCE_SOURCE=" + str(receipt.get("source")))
    print("VERDICT=VERIFIED_EDITORIAL_DRAFT_REVIEW_REQUIRED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
