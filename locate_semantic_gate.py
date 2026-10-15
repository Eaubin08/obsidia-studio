"""Locate the exact local source of Brody's pre-reasoning status, read-only.

Usage: python locate_semantic_gate.py
No imports or execution of Jarvis modules, no writes.
"""
import argparse
from pathlib import Path

TERMS = (
    "BRODY_PRE_REASONING_RESOLUTION_REQUIRED",
    "SEMANTIC_RESOLUTION_REQUIRED",
    "ROUTE_IR_CLOSURE_CRITICAL_MISSING",
)


def scan(root: Path):
    matches = []
    for folder in ("apps/obsidia_api", "scripts", "periphery"):
        base = root / folder
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            if any(part in ("__pycache__", ".venv", "site-packages") for part in path.parts):
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines):
                if any(term in line for term in TERMS):
                    matches.append((path.relative_to(root).as_posix(), i + 1, lines[max(0, i - 8):i + 9]))
    return matches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jarvis", type=Path,
                        default=Path.home() / "Desktop" / "obsidia-jarvis-advanced-integration-v0")
    args = parser.parse_args()
    root = args.jarvis.resolve()
    print("MODE=LOCAL_SOURCE_READ_ONLY")
    print("SOURCE_ROOT=" + str(root))
    found = scan(root)
    if not found:
        print("VERDICT=STATUS_LITERALS_NOT_FOUND_IN_SCANNED_SOURCE")
        return
    for path, line, lines in found[:30]:
        print("\nFILE=" + path + " LINE=" + str(line))
        for item in lines:
            print(item[:280])
    print("\nMATCH_COUNT=" + str(len(found)))
    print("VERDICT=SEMANTIC_GATE_SOURCE_LOCATED")


if __name__ == "__main__":
    main()
