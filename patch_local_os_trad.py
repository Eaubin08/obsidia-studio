"""AST-scoped repair of one lexical OS Trad false-positive, never a HOLD override.

Dry-run by default. --apply snapshots the existing file before editing.
Only patches a known _risk_flags definition ending with return flags or
return adjust_risk_flags(text, flags). Refuses unfamiliar implementations.
"""
import argparse
import ast
from pathlib import Path

TARGET = Path("apps/obsidia_api/routes/os_trad_ir_reverse.py")

HELPER = '''
def _studio_explanatory_action_filter(text, flags):
    """Remove only the lexical 'agir' false-positive in explicit explanations.

    Do NOT relax real execution requests, memory writes, mutations, or
    ambiguous prompts. Other risk flags are preserved without changes.
    """
    import re
    if not isinstance(flags, list) or "action_request" not in flags:
        return flags
    s = text.casefold().strip()
    # Positive explanatory question shape, not an arbitrary appearance of
    # a question word somewhere in an action request.
    explanatory = re.match(
        r"^(?:pourquoi|comment|en quoi|why|how)\\b", s
    )
    if not explanatory or not re.search(r"\\bagir\\b", s):
        return flags
    # Any executable directive or privileged operation keeps the flag.
    forbidden = re.search(
        r"\\b(?:agis|publie|poste|envoie|supprime|efface|lance|"
        r"exécute|execute|transfère|transfer|send|write|save|"
        r"commit|push|modifie|patch|déploie|deploy|"
        r"graphiti|neo4j|memory_write)\\b", s
    )
    if forbidden or any(
        flag in flags for flag in
        ("write_request", "mutation_request", "memory_write_request",
         "canon_promotion_request", "authority_claim")
    ):
        return flags
    return [flag for flag in flags if flag != "action_request"]
'''


def patch_source(source):
    tree = ast.parse(source)
    if any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
           and n.name == "_studio_explanatory_action_filter"
           for n in tree.body):
        raise RuntimeError("ALREADY_PATCHED: no second application")
    functions = [n for n in tree.body
                 if isinstance(n, ast.FunctionDef) and n.name == "_risk_flags"]
    if len(functions) != 1:
        raise RuntimeError("SOURCE_MISMATCH: missing or duplicate _risk_flags")
    fn = functions[0]
    if len(fn.args.args) != 1 or fn.args.args[0].arg != "text":
        raise RuntimeError("SOURCE_MISMATCH: unexpected function signature")
    if not fn.body or not isinstance(fn.body[-1], ast.Return):
        raise RuntimeError("SOURCE_MISMATCH: no final return")
    returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
    if len(returns) != 1:
        raise RuntimeError("SOURCE_MISMATCH: multiple returns")
    value = fn.body[-1].value
    valid = isinstance(value, ast.Name) and value.id == "flags"
    valid |= (isinstance(value, ast.Call)
              and isinstance(value.func, ast.Name)
              and value.func.id == "adjust_risk_flags"
              and len(value.args) == 2
              and isinstance(value.args[0], ast.Name)
              and value.args[0].id == "text"
              and isinstance(value.args[1], ast.Name)
              and value.args[1].id == "flags"
              and not value.keywords)
    if not valid or "action_request" not in ast.get_source_segment(source, fn):
        raise RuntimeError("SOURCE_MISMATCH: unrecognized risk classifier")
    lines = source.splitlines(keepends=True)
    node = fn.body[-1]
    if node.lineno != node.end_lineno:
        raise RuntimeError("SOURCE_MISMATCH: multiline return")
    original_line = lines[node.lineno - 1]
    indent = original_line[:len(original_line) - len(original_line.lstrip())]
    replacement = ast.get_source_segment(source, value)
    lines[node.lineno - 1] = (
        indent + "return _studio_explanatory_action_filter(text, "
        + replacement + ")" + ("\\r\\n" if original_line.endswith("\\r\\n") else "\\n")
    )
    ending = "\\r\\n" if "\\r\\n" in source else "\\n"
    result = "".join(lines) + ending + HELPER.strip().replace("\\n", ending) + ending
    ast.parse(result)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jarvis", type=Path, default=Path.home() / "Desktop" / "obsidia-jarvis-advanced-integration-v0")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    target = args.jarvis.resolve() / TARGET
    if not target.is_file():
        raise SystemExit("STOP: Jarvis OS Trad source not found: " + str(target))
    raw = target.read_bytes()
    try:
        original = raw.decode("utf-8")
        patched = patch_source(original)
    except (UnicodeDecodeError, RuntimeError, SyntaxError) as exc:
        raise SystemExit("STOP: " + str(exc))
    if not args.apply:
        print("DRY_RUN=PASS; file=" + str(target))
        print("CHANGE=filter confirmed explanatory false positive only")
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
