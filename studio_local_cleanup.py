"""Restore ONLY the two Studio-originated edits to the local Jarvis tree.

Dry-run by default. Strict fail-closed comparison: never overwrite changes
made after Studio's patch. No Git reset, no repo-wide operations.
"""
from pathlib import Path
import argparse
import ast
import difflib

FILES = (
    ("apps/obsidia_api/routes/os_trad_ir_reverse.py", ".studio_before_fix.bak", "os_trad"),
    ("periphery/language/unknown_qualifier.py", ".studio_surface_v1.bak", "surface"),
)

def validate_current(kind, current, original):
    if kind == "surface":
        marker = "# OBSIDIA_STUDIO_EDITORIAL_SURFACE_V1"
        if current.count(marker) != 1:
            raise ValueError("Studio surface marker missing/duplicated")
        tree = ast.parse(current)
        lines = current.splitlines(keepends=True)
        start = next(i for i, line in enumerate(lines) if marker in line)
        if start + 1 >= len(lines) or not lines[start+1].startswith("_COMMON_SURFACE_WORDS.update({"):
            raise ValueError("unexpected surface patch shape")
        end = next((i for i in range(start+2, len(lines)) if lines[i].strip() == "})"), None)
        if end is None:
            raise ValueError("surface patch end missing")
        recovered = "".join(lines[:start] + lines[end+1:])
        # Our patch inserted a blank line before marker; remove only that line.
        rlines = recovered.splitlines(keepends=True)
        if start > 0 and rlines[start-1].strip() == "":
            del rlines[start-1]
        recovered = "".join(rlines)
        return recovered
    # OS Trad patch was a function-body rewrite plus a helper appended at EOF.
    if kind == "os_trad":
        marker = "def _studio_explanatory_action_filter(text, flags):"
        if current.count(marker) != 1:
            raise ValueError("Studio OS Trad helper missing/duplicated")
        if "_studio_explanatory_action_filter(text, " not in current:
            raise ValueError("Studio OS Trad call missing")
        # Do not attempt to reverse a dynamic AST change with guesses.
        return None
    raise ValueError("unexpected patch kind")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jarvis", type=Path, default=Path.home() / "Desktop" / "obsidia-jarvis-advanced-integration-v0")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = args.jarvis.resolve()
    plans = []
    for rel, suffix, kind in FILES:
        target = root / rel
        backup = target.with_suffix(target.suffix + suffix)
        if not target.is_file() or not backup.is_file():
            raise SystemExit("STOP_MISSING_FILE_OR_BACKUP=" + rel)
        current_bytes = target.read_bytes()
        original_bytes = backup.read_bytes()
        if current_bytes == original_bytes:
            print("ALREADY_CLEAN=" + rel)
            continue
        try:
            current = current_bytes.decode("utf-8")
            original = original_bytes.decode("utf-8")
            ast.parse(current)
            ast.parse(original)
            candidate = validate_current(kind, current, original)
            if candidate is not None and candidate != original:
                raise ValueError("additional changes detected after Studio patch")
            # For OS Trad, exact patch reconstruction from backup is mandatory.
            if kind == "os_trad":
                from pathlib import Path as _Path
                # This recovery file stays in Studio. The archived patch is NOT
                # executed; it is read as text and checked via AST.
                patch_file = _Path(__file__).resolve().parent / "patch_local_os_trad.py"
                if not patch_file.exists():
                    raise ValueError("OS Trad patch definition unavailable: STOP")
                scope = {"__name__": "_studio_patch_validation_"}
                exec(compile(patch_file.read_text(encoding="utf-8"), str(patch_file), "exec"), scope)
                expected = scope["patch_source"](original)
                if expected.encode("utf-8") != current_bytes:
                    raise ValueError("OS Trad has diverged from Studio patch")
            else:
                # Exact match is required, not just AST-equivalence.
                from pathlib import Path as _Path
                patch_file = _Path(__file__).resolve().parent / "patch_local_unknown_surface.py"
                if not patch_file.exists():
                    raise ValueError("surface patch definition unavailable: STOP")
                scope = {"__name__": "_studio_patch_validation_"}
                exec(compile(patch_file.read_text(encoding="utf-8"), str(patch_file), "exec"), scope)
                if scope["patch_source"](original).encode("utf-8") != current_bytes:
                    raise ValueError("surface file diverged from Studio patch")
        except (ValueError, SyntaxError, UnicodeDecodeError, RuntimeError) as exc:
            raise SystemExit("STOP_DIVERGED=" + rel + ": " + str(exc))
        plans.append((target, original_bytes))
        print("RESTORABLE_EXACT_STUDIO_PATCH=" + rel)
    if not args.apply:
        print("DRY_RUN=PASS; eligible=" + str(len(plans)))
        return
    for target, original_bytes in plans:
        target.write_bytes(original_bytes)
        print("RESTORED=" + str(target))
    print("RESTORE_COMPLETE; restart affected services")


if __name__ == "__main__":
    main()
