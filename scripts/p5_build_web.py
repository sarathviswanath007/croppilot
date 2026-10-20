"""Tasks 4.02, 5.25, 5.28: prepare the web app in web/ and scan it for guarantee language.

Copies data/engine_data.json to web/data/engine_data.json, then scans every .html, .js and .css
file in web/ plus every string in engine_data.json against config/banned_words.json (FR-19,
AC-09). Any hit fails the build. The web/ folder is then a complete static site: upload it as-is
to any static host (no server code, no build tools).

Usage: python3 scripts/p5_build_web.py
"""
import json
import re
import shutil
import sys

from p2_asof import DATA, ROOT

WEB = ROOT / "web"


def strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)


def scan(name, text, cfg):
    low = text.lower()
    for phrase in cfg["allowed_phrases"]:
        low = low.replace(phrase.lower(), " ")
    hits = []
    for word in cfg["banned"]:
        pattern = re.escape(word) if not word.isascii() else r"(?<![\w.-])" + re.escape(word) + r"(?![\w.-])"
        for m in re.finditer(pattern, low):
            hits.append(f"{name}:{low.count(chr(10), 0, m.start()) + 1}: '{word}'")
    return hits


def build():
    cfg = json.loads((ROOT / "config" / "banned_words.json").read_text())
    (WEB / "data").mkdir(exist_ok=True)
    shutil.copyfile(DATA / "engine_data.json", WEB / "data" / "engine_data.json")
    hits = []
    for f in sorted(WEB.rglob("*")):
        if f.suffix in (".html", ".js", ".css"):
            hits += scan(str(f.relative_to(ROOT)), f.read_text(), cfg)
    data = json.loads((WEB / "data" / "engine_data.json").read_text())
    hits += scan("engine_data.json strings", "\n".join(strings(data)), cfg)
    if hits:
        print("Banned-word scan FAILED:\n  " + "\n  ".join(hits))
        sys.exit(1)
    size = sum(f.stat().st_size for f in WEB.rglob("*") if f.is_file())
    print(f"web/ ready: banned-word scan 0 hits, {size / 1024:.0f} KB in total")


if __name__ == "__main__":
    build()
