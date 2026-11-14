#!/usr/bin/env python3
"""Run a verification command and keep a VERIFY_FAILED.txt marker in sync with the result.

  python verify_marker.py --dir OUTPUT_DIR -- <check command and arguments>

Command exits 0  -> marker removed (if present), exit 0
Command exits !=0 -> marker written with the command, exit code and the tail of its output, exit 1
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MARKER = "VERIFY_FAILED.txt"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True, help="folder that holds the output being verified")
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="-- followed by the check command")
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        ap.error("no check command given")

    marker = Path(a.dir) / MARKER
    Path(a.dir).mkdir(parents=True, exist_ok=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        marker.unlink(missing_ok=True)
        print("check passed; marker cleared")
        return 0
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-30:])
    marker.write_text(
        f"Verification FAILED at {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"Command: {' '.join(cmd)}\nExit code: {r.returncode}\n\nOutput (tail):\n{tail}\n",
        encoding="utf-8",
    )
    print(f"check FAILED; wrote {marker}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
