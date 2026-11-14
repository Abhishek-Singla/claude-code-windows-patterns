#!/usr/bin/env python3
"""Fingerprint a set of input files so a job can skip work when nothing changed.

  python fingerprint.py check  --state STATE.json --files "glob" ["glob" ...] [--hash]
      exit 0 = unchanged (skip), exit 1 = changed or no stored state (rebuild)
  python fingerprint.py update --state STATE.json --files "glob" ["glob" ...] [--hash]
      store the current fingerprint (call this only AFTER the rebuild and its checks pass)
"""
import argparse
import glob
import hashlib
import json
import os
import sys
from pathlib import Path


def fingerprint(patterns: list[str], use_hash: bool) -> dict:
    files = sorted({p for pat in patterns for p in glob.glob(pat, recursive=True) if os.path.isfile(p)})
    entries = {}
    for p in files:
        st = os.stat(p)
        entry: dict = {"size": st.st_size, "mtime_ns": st.st_mtime_ns}
        if use_hash:
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            entry["sha256"] = h.hexdigest()
        entries[p.replace("\\", "/")] = entry
    return {"hash_mode": use_hash, "files": entries}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "update"])
    ap.add_argument("--state", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--hash", action="store_true", help="also compare SHA-256 content hashes")
    a = ap.parse_args()

    current = fingerprint(a.files, a.hash)
    state = Path(a.state)
    if a.cmd == "update":
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(current, indent=2), encoding="utf-8")
        print(f"stored fingerprint of {len(current['files'])} file(s)")
        return 0

    if not state.exists():
        print("no stored state: rebuild")
        return 1
    stored = json.loads(state.read_text(encoding="utf-8"))
    if stored == current:
        print(f"unchanged ({len(current['files'])} file(s)): skip")
        return 0
    old, new = set(stored["files"]), set(current["files"])
    changed = [f for f in old & new if stored["files"][f] != current["files"][f]]
    print(f"changed: +{len(new - old)} added, -{len(old - new)} removed, ~{len(changed)} modified: rebuild")
    return 1


if __name__ == "__main__":
    sys.exit(main())
