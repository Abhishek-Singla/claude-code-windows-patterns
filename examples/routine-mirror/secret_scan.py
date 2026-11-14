#!/usr/bin/env python3
"""Scan a folder before it is committed to a public mirror. Exit 1 if anything suspicious is found.

Blocks: key/token shapes, e-mail addresses, absolute user-profile paths, cloud bucket URLs
with real-looking names are NOT special-cased: use placeholders such as gs://example-bucket.
Also blocks file types that must never be mirrored.

Usage: python secret_scan.py <folder>
"""
import re
import sys
from pathlib import Path

BANNED_SUFFIXES = {".xlsx", ".csv", ".pdf", ".docx", ".zip", ".feature", ".env", ".pem", ".key", ".pfx"}
PATTERNS = [
    ("API key / token", re.compile(r"\b(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35})\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("e-mail address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("user-profile path", re.compile(r"[A-Za-z]:\\+Users\\+[^\\\s\"']+|/(?:home|Users)/[^/\s\"']+/")),
    ("password assignment", re.compile(r"(?i)\b(?:password|passwd|secret|token)\s*[:=]\s*['\"][^'\"\s]{6,}['\"]")),
]


def scan(root: Path) -> list[str]:
    problems = []
    for p in root.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        rel = p.relative_to(root)
        if p.suffix.lower() in BANNED_SUFFIXES:
            problems.append(f"{rel}: file type must not be mirrored")
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for label, rx in PATTERNS:
                if rx.search(line):
                    problems.append(f"{rel}:{n}: possible {label}")
    return problems


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    found = scan(Path(sys.argv[1]))
    for p in found:
        print(p)
    print(f"{len(found)} problem(s)" if found else "clean")
    raise SystemExit(1 if found else 0)
