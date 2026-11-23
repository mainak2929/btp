"""Write the website as a standalone static site (for GitHub Pages or any web host).

    python website/export_site.py ../personal-sip-planner

index.html here is a page body (the claude.ai preview adds <html>/<head> itself), so this wraps it
in a full HTML document and copies sip.js and data.js beside it.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPLIT = '<div class="wrap">'


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    page = (HERE / "index.html").read_text(encoding="utf-8")
    head, body = page.split(SPLIT, 1)
    doc = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
           + head.rstrip() + "\n<style>body{margin:0}[hidden]{display:none!important}</style>\n"
           "</head>\n<body>\n" + SPLIT + body.rstrip() + "\n</body>\n</html>\n")
    (out / "index.html").write_text(doc, encoding="utf-8")
    for f in ("sip.js", "data.js"):
        shutil.copy(HERE / f, out / f)
    print(f"Wrote {out / 'index.html'}, sip.js, data.js")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "site")
