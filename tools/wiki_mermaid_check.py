#!/usr/bin/env python3
"""Scan Markdown files for broken ```mermaid blocks using mermaid-cli (mmdc).

Usage:
  python3 check_mermaid.py [ROOT] [--mmdc PATH] [--jobs N]

Outputs a JSON report of every failing mermaid block with file, block index,
line number and the parser error. Exits non-zero if any block fails.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor

FENCE_RE = re.compile(r"```mermaid\n(.*?)```", re.S)


def extract_blocks(path):
    text = open(path, encoding="utf-8").read()
    blocks = []
    offset = 0
    for m in FENCE_RE.finditer(text):
        start = m.start(1)
        line = text.count("\n", 0, start) + 1
        blocks.append((line, m.group(1)))
    return blocks


def check_one(args):
    mmdc, block = args
    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as f:
        f.write(block)
        path = f.name
    out = path + ".svg"
    try:
        proc = subprocess.run(
            [mmdc, "-i", path, "-o", out],
            capture_output=True, text=True, timeout=120,
        )
        err = proc.stderr
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT: mmdc exceeded 120s"
    finally:
        os.unlink(path)
        if os.path.exists(out):
            os.unlink(out)
    if rc != 0 or "Parse error" in err:
        lines = err.strip().splitlines()
        # Keep the diagnostic block: from the first "Error"/"Parse" line
        # down to the "Expecting ... got" line (or the whole tail).
        keep = []
        for ln in lines:
            if keep or "Error" in ln or "Parse" in ln or "Expecting" in ln:
                keep.append(ln)
            if "Expecting" in ln:
                break
        return "\n".join(keep) if keep else "\n".join(lines[-6:])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="develop/wiki")
    ap.add_argument("--mmdc", default="mmdc")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    files = []
    for dp, _, fns in os.walk(args.root):
        for fn in fns:
            if fn.endswith(".md"):
                files.append(os.path.join(dp, fn))

    tasks = []
    meta = []
    for fp in files:
        for idx, (line, block) in enumerate(extract_blocks(fp)):
            meta.append((fp, idx, line))
            tasks.append((args.mmdc, block))

    results = {}
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        for (fp, idx, line), err in zip(meta, ex.map(check_one, tasks)):
            if err:
                results.setdefault(fp, []).append(
                    {"block": idx, "line": line, "error": err}
                )

    print(json.dumps(results, indent=2, ensure_ascii=False))
    if results:
        total = sum(len(v) for v in results.values())
        print(f"\n{total} broken blocks in {len(results)} files", file=sys.stderr)
        sys.exit(1)
    print("All mermaid blocks OK", file=sys.stderr)


if __name__ == "__main__":
    main()
