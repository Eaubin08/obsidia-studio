"""Test Studio cognitive generation without the UI or post/image writes.

Run: python diagnose_generation.py --subject "Pourquoi une IA doit vérifier avant d'agir ?"
Does not change upstream authority classification, retry HOLD, or call Qwen directly.
"""
import argparse
import json
import os
import sys

import studio_ai


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
    prompt = (
        "Proposition de texte éditorial consultatif pour LinkedIn, en français. "
        "Sujet : " + opts.subject.strip() + ". "
        "Contenu destiné à une relecture humaine, fondé sur les seuls faits fournis."
    )
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
    suff = result.get("brody_sufficiency") or {}
    route = result.get("route_decision") or {}
    if suff.get("status") == "GOVERNANCE_BOUNDARY" or route.get("gate_verdict") in ("HOLD", "BLOCK"):
        print("VERDICT=UPSTREAM_GOVERNANCE_BOUNDARY_NOT_STUDIO_PARSER")
        return 3
    if not details["final_answer_present"]:
        print("VERDICT=NO_EDITORIAL_MATERIAL")
        return 4
    print("VERDICT=COGNITIVE_MATERIAL_PRESENT_REVIEW_REQUIRED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
