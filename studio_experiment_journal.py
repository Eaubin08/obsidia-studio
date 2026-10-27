"""LOT 1 metadata only. No text, receipts, references, credentials or exception messages."""
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import uuid

from studio_e11_contract import (BASELINE_CHECKPOINT, PREVIOUS_CHECKPOINT, CHECKPOINT, SCHEMA,
                                ERROR_CODES, STATUSES, diagnostic_summary)

ROOT = Path(__file__).resolve().parent
JOURNAL_PATH = ROOT / "data" / "experiments" / "e11_lot1" / "events.jsonl"
JOURNAL_FIELDS = frozenset({"experiment_id", "date", "consumer_version", "checkpoint_initial",
    "checkpoint_previous", "checkpoint_configured", "checkpoint_verified", "service_verification",
    "status", "error_code", "counts", "elapsed_ms", "response_bytes"}) | frozenset(diagnostic_summary({}))


def record_experiment(result, *, elapsed_ms, response_bytes):
    """Construct the event by allowlist; never merge the caller's dictionary."""
    experiment_id = str(uuid.UUID(result["experiment_id"]))
    status, code = result["consumer_status"], result["error_code"]
    if status not in STATUSES or code not in ERROR_CODES:
        raise ValueError("INVALID_JOURNAL_METADATA")
    if type(response_bytes) is not int or response_bytes < 0:
        raise ValueError("INVALID_JOURNAL_METADATA")
    if type(elapsed_ms) not in (int, float) or not math.isfinite(elapsed_ms) or elapsed_ms < 0:
        raise ValueError("INVALID_JOURNAL_METADATA")
    context = result.get("e11_context") or {}
    packet = context.get("context_packet") or {}
    verification = (result.get("provenance") or {}).get("service_verification") or {}
    verified = (verification.get("status") == "TECHNICAL_SNAPSHOT_VERIFIED"
                and verification.get("checkpoint") == CHECKPOINT)
    event = {"experiment_id": experiment_id, "date": datetime.now(timezone.utc).isoformat(),
        "consumer_version": SCHEMA, "checkpoint_initial": BASELINE_CHECKPOINT,
        "checkpoint_previous": PREVIOUS_CHECKPOINT,
        "checkpoint_configured": CHECKPOINT, "checkpoint_verified": CHECKPOINT if verified else None,
        "service_verification": "TECHNICAL_SNAPSHOT_VERIFIED" if verified else "UNVERIFIED",
        "status": status, "error_code": code,
        "counts": {"memory_entries": len(context.get("memory_entries") or []),
                   "unknowns": len(packet.get("unknowns") or []), "omitted": len(packet.get("omitted") or [])},
        "elapsed_ms": round(elapsed_ms, 3), "response_bytes": response_bytes,
        **diagnostic_summary(result)}
    # A misconfigured/symlinked path must never redirect a write to a producer.
    target = JOURNAL_PATH.resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError("JOURNAL_OUTSIDE_STUDIO")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.parent.resolve() != target.parent or (target.exists() and target.is_symlink()):
        raise ValueError("JOURNAL_PATH_INVALID")
    line = (json.dumps(event, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
    fd = os.open(target, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o600)
    try:
        if os.fstat(fd).st_nlink != 1:
            raise ValueError("JOURNAL_LINK_REFUSED")
        if os.write(fd, line) != len(line):
            raise OSError("JOURNAL_WRITE_INCOMPLETE")
    finally:
        os.close(fd)
