"""Bounded local repair of lexical surface words in Brody's qualifier.

Dry run unless --apply. Does not alter unresolved concepts, router decisions,
semantic closure gates, KX108 authority or Qwen permission.
"""
import argparse
import ast
from pathlib import Path

TARGET = Path("periphery/language/unknown_qualifier.py")
# Words describe editorial instructions / grammatical surface, not domain facts.
WORDS = (
    "francais", "brouillon", "consultatif", "linkedin", "sujet",
    "suivant", "doit", "avant", "presenter", "uniquement",
    "faits", "disponibles",
)
MARKER = "# OBSIDIA_STUDIO_EDITORIAL_SURFACE_V1"


def patch_source(source):
    tree = ast.parse(source)
    if MARKER in source:
        raise RuntimeError("ALREADY_PATCHED")
    names = [n for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "_COMMON_SURFACE_WORDS"
                     for t in n.targets)]
    if len(names) != 1 or not isinstance(names[0].value, ast.Set):
        raise RuntimeError("SOURCE_MISMATCH: expected one literal common-surface set")
    node = names[0]
    # Preserve entire existing vocabulary. Add only surface-language terms,
    # never a model-decided whitelist, and never reinterpret unknown concepts.
    lines = source.splitlines(keepends=True)
    ending = "\r\n" if "\r\n" in source else "\n"
    extra = ending + MARKER + ending + "_COMMON_SURFACE_WORDS.update({" + ending
    extra += "".join("    " + repr(w) + "," + ending for w in WORDS)
    extra += "})" + ending
    # Insert immediately after original set definition.
    lines.insert(node.end_lineno, extra)
    patched = "".join(lines)
    ast.parse(patched)
    return patched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jarvis", type=Path,
                        default=Path.home() / "Desktop" / "obsidia-jarvis-advanced-integration-v0")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    target = args.jarvis.resolve() / TARGET
    if not target.is_file():
        raise SystemExit("STOP: missing " + str(target))
    raw = target.read_bytes()
    try:
        patched = patch_source(raw.decode("utf-8-sig"))
    except (SyntaxError, UnicodeError, RuntimeError) as exc:
        raise SystemExit("STOP: " + str(exc))
    if not args.apply:
        print("DRY_RUN=PASS")
        print("SURFACE_TERMS=" + ",".join(WORDS))
        print("UNKNOWN_CONCEPT_POLICY=UNCHANGED")
        return
    backup = target.with_suffix(target.suffix + ".studio_surface_v1.bak")
    if backup.exists():
        raise SystemExit("STOP: backup exists " + str(backup))
    backup.write_bytes(raw)
    try:
        target.write_bytes(patched.encode("utf-8"))
    except Exception:
        target.write_bytes(raw)
        raise
    print("APPLIED=" + str(target))
    print("BACKUP=" + str(backup))
    print("RESTART_GATEWAY_REQUIRED=TRUE")


if __name__ == "__main__":
    main()
