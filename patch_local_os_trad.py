"""Surgical local OS Trad classifier repair, shipped WITH Studio.

Default dry run. --apply requires a compatible Jarvis source and creates
a byte-for-byte .bak file. Does not modify KX108, AMD, or an authority verdict.
"""
import argparse
import ast
from pathlib import Path

TARGET = Path("apps/obsidia_api/routes/os_trad_ir_reverse.py")
OLD = '''    _action_tokens = ["agir", "lance", "execute", "exécute", "send", "transfer", "write"]
    _has_action = (
        any(token in low for token in _action_tokens)
        or bool(re.search(r"\\bact\\b", low))
    )
    if _has_action and not _action_negation:
        flags.append("action_request")
'''
NEW = '''    # Studio readonly editorial contract: mentioning "agir" in a question
    # about agency is not an instruction to execute an action.
    # Keep real execution verbs and imperative action requests gated.
    _action_verbs = r"\\b(?:lance|execute|exécute|send|transfer|write|act)\\b"
    _has_action = bool(re.search(_action_verbs, low))
    _agir_mentioned = bool(re.search(r"\\bagir\\b", low))
    _explanatory_question = bool(re.search(
        r"\\b(?:pourquoi|comment|expliquer|explanation|why|how)\\b", low
    ))
    _explicit_execution = bool(re.search(
        r"\\b(?:agis|execute|exécute|publie|envoie|transfère|lance)\\b",
        low,
    ))
    if (_has_action or (_agir_mentioned and not _explanatory_question)
            or _explicit_execution) and not _action_negation:
        flags.append("action_request")
'''


def patch_source(source: str) -> str:
    if source.count(OLD) != 1:
        raise RuntimeError("SOURCE_MISMATCH: exact OS Trad classifier block not found; no write")
    new_source = source.replace(OLD, NEW, 1)
    ast.parse(new_source)
    return new_source


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jarvis", type=Path, default=Path.home() / "Desktop" / "obsidia-jarvis-advanced-integration-v0")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    target = args.jarvis.resolve() / TARGET
    if not target.is_file():
        raise SystemExit("STOP: Jarvis OS Trad file not found: " + str(target))
    raw = target.read_bytes()
    try:
        original = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit("STOP: source is not UTF-8") from exc
    try:
        patched = patch_source(original)
    except (RuntimeError, SyntaxError) as exc:
        raise SystemExit("STOP: " + str(exc))
    if not args.apply:
        print("DRY_RUN=PASS; file=" + str(target))
        print("NEXT=rerun with --apply after reviewing this change")
        return
    backup = target.with_suffix(target.suffix + ".studio_before_fix.bak")
    if backup.exists():
        raise SystemExit("STOP: backup already exists: " + str(backup))
    backup.write_bytes(raw)
    try:
        target.write_bytes(patched.encode("utf-8"))
    except Exception:
        target.write_bytes(raw)
        raise
    print("PATCH_APPLIED=" + str(target))
    print("BACKUP=" + str(backup))
    print("RESTART_GATEWAY_REQUIRED=TRUE")


if __name__ == "__main__":
    main()
