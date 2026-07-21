#!/usr/bin/env python3
"""Batch-fix broken ```mermaid blocks in a Markdown tree.

Strategy: for every mermaid block that fails `mmdc` validation, try a series
of safe normalisation rules. A transform is kept ONLY if it reduces (or keeps
zero) parser errors, so a passing diagram is never degraded.

Safe, validated transforms:
  R1  Strip zero-width / BOM chars (U+200B/200C/200D/FEFF) that break the
      ```mermaid fence so GitHub renders it as plain code.
  R2  Quote node/shape labels that contain characters mermaid treats as
      syntax (| ( ) { } " / , < > & # ; =) and are not already quoted.
  R3  Quote labels that contain a nested '[' (e.g. DS[Storage[Medium]]).
  R4  Space out dotted-edge labels:  -.label.->  ->  -. "label" .->

Usage:
  python3 wiki_mermaid_fix.py [ROOT] [--mmdc PATH] [--jobs N] [--dry-run]
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor

FENCE_RE = re.compile(r"```mermaid\n(.*?)```", re.S)
ZERO_WIDTH = ["\u200b", "\u200c", "\u200d", "\ufeff"]
RISKY = re.compile(r"[|(){}?\"/,<>&#;=]")

SHAPE_OPEN = ["((", "([", "[(", "[[", "[(]", "[@", "[", "(", "{"]
# longest openers first so we match the right one
_BRACKET = {
    "[": ("[", "]"),
    "(": ("(", ")"),
    "{": ("{", "}"),
    "((": ("(", "))"),
    "([": ("(", "])"),
    "[(": ("(", ")]"),
    "[[": ("[", "]]"),
    "[(]": ("(", ")]"),
    "[@": ("[", "]"),
}


def _quote_labels(block):
    """Wrap unquoted shape labels containing risky chars in double quotes."""
    out = []
    i = 0
    n = len(block)
    while i < n:
        matched = None
        for op in SHAPE_OPEN:
            if block[i:].startswith(op):
                matched = op
                break
        if not matched:
            out.append(block[i])
            i += 1
            continue
        open_ch, close_str = _BRACKET[matched]
        depth = 0
        j = i + len(matched)
        end = -1
        while j < n:
            ch = block[j]
            if ch == open_ch:
                depth += 1
            elif ch == close_str[0]:
                if depth == 0:
                    end = j
                    break
                depth -= 1
            j += 1
        if end == -1:
            out.append(block[i])
            i += 1
            continue
        inner = block[i + len(matched):end]
        # Already quoted? leave untouched.
        if inner.startswith('"') and inner.endswith('"') and len(inner) >= 2:
            out.append(block[i:end + len(close_str)])
        else:
            qs = inner.replace('"', "'")
            out.append(matched + '"' + qs + '"' + close_str)
        i = end + len(close_str)
    return "".join(out)


def _fix_block(block):
    rules = []
    # R1 zero-width strip
    s1 = block
    for z in ZERO_WIDTH:
        s1 = s1.replace(z, "")
    if s1 != block:
        rules.append(s1)
    # R4 dotted-edge label spacing (do before quoting so quotes land inside)
    s4 = re.sub(r"-\.([^.\n]+?)\.->", lambda m: '-. "%s" .->' % m.group(1).strip(), s1)
    if s4 != s1:
        rules.append(s4)
    # R2/R3 quote risky / nested labels
    s2 = _quote_labels(s4)
    if s2 != s4:
        rules.append(s2)
    # de-dup while preserving order
    seen = set()
    ordered = []
    for r in rules:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    return ordered


def _validate(mmdc, block):
    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as f:
        f.write(block)
        path = f.name
    out = path + ".svg"
    try:
        proc = subprocess.run(
            [mmdc, "-i", path, "-o", out],
            capture_output=True, text=True, timeout=120,
        )
        return proc.returncode == 0 and "Parse error" not in proc.stderr
    except subprocess.TimeoutExpired:
        return False
    finally:
        os.unlink(path)
        if os.path.exists(out):
            os.unlink(out)


def _blocks_of(path):
    txt = open(path, encoding="utf-8").read()
    return txt, list(FENCE_RE.finditer(txt))


def _fix_one(args):
    mmdc, path = args
    txt, matches = _blocks_of(path)
    if not matches:
        return None
    new_txt = txt
    changed = False
    for m in matches:
        block = m.group(1)
        if _validate(mmdc, block):
            continue
        candidates = _fix_block(block)
        fixed = None
        for cand in candidates:
            if _validate(mmdc, cand):
                fixed = cand
                break
        if fixed is not None and fixed != block:
            new_txt = new_txt.replace(block, fixed, 1)
            changed = True
    if changed:
        return new_txt
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="develop/wiki")
    ap.add_argument("--mmdc", default="mmdc")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = []
    for dp, _, fns in os.walk(args.root):
        for fn in fns:
            if fn.endswith(".md"):
                files.append(os.path.join(dp, fn))

    fixed_files = []
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        for fp, res in zip(files, ex.map(_fix_one, [(args.mmdc, f) for f in files])):
            if res is None:
                continue
            fixed_files.append(fp)
            if args.dry_run:
                print(f"[dry-run] would fix: {fp}")
            else:
                open(fp, "w", encoding="utf-8").write(res)
                print(f"fixed: {fp}")

    print(f"\n{len(fixed_files)} file(s) fixed" if fixed_files
          else "\nno fixes needed")


if __name__ == "__main__":
    main()
