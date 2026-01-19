import re
from pathlib import Path
from datetime import datetime

ROOT = Path(".")
FILES = [ROOT/"index.html"]
CASE_DIR = ROOT/"case"
CSS = ROOT/"styles.css"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

def backup(p: Path):
    if p.exists():
        bp = p.with_suffix(p.suffix + f".bak-{STAMP}")
        bp.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

WA_SVG = r'''
<svg class="wa-fab__svg" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
  <path d="M16.02 3C9.39 3 4 8.2 4 14.6c0 2.23.8 4.3 2.14 5.97L5 29l8.65-1.88c1.26.35 2.58.54 3.95.54 6.63 0 12.02-5.2 12.02-11.6C29.62 8.2 22.65 3 16.02 3zm0 2.26c5.3 0 9.6 4.03 9.6 9.0s-4.3 9-9.6 9c-1.22 0-2.4-.2-3.5-.6l-.68-.24-5.14 1.12 1.33-4.84-.45-.6c-1.07-1.42-1.64-3.08-1.64-4.84 0-4.97 4.3-9 9.6-9zm-4.3 5.3c-.22 0-.58.08-.88.4-.3.32-1.15 1.1-1.15 2.67 0 1.57 1.18 3.1 1.35 3.3.17.2 2.32 3.62 5.72 4.93 2.82 1.1 3.4.88 4.02.82.62-.06 2.02-.8 2.3-1.57.28-.78.28-1.44.2-1.57-.08-.13-.3-.2-.62-.35-.32-.15-2.02-1-2.33-1.12-.3-.12-.53-.2-.75.12-.22.32-.87 1.12-1.07 1.35-.2.23-.4.26-.72.1-.32-.15-1.33-.48-2.53-1.53-.93-.82-1.56-1.83-1.74-2.15-.18-.32-.02-.5.13-.66.14-.16.32-.4.48-.6.16-.2.2-.35.32-.58.12-.23.06-.43-.02-.6-.08-.17-.73-1.9-1.03-2.6-.26-.6-.55-.62-.75-.62h-.63z"/>
</svg>
'''.strip()

def ensure_css(css: str) -> str:
    if "/* === WA SVG FIX === */" in css:
        return css
    block = r"""
/* === WA SVG FIX === */
/* Sticky WhatsApp: cerchio, solo icona, SVG premium */
.wa-fab{
  width: 58px;
  height: 58px;
  padding: 0 !important;
  border-radius: 999px !important;
  justify-content: center !important;
  gap: 0 !important;
}
.wa-fab__text{ display:none !important; }
.wa-fab__icon{
  width: 46px;
  height: 46px;
  padding: 0;
  background: rgba(37, 211, 102, .22);
  border: 1px solid rgba(37, 211, 102, .35);
  border-radius: 999px;
  display: grid;
  place-items: center;
}
.wa-fab__svg{
  width: 24px;
  height: 24px;
  fill: rgba(233, 238, 251, 0.95);
}

/* mobile: resta cerchio, non pill largo */
@media (max-width: 520px){
  .wa-fab{
    left: auto !important;
    right: 18px !important;
    bottom: 18px !important;
  }
}
"""
    return css + "\n" + block

def replace_fab_inner(html: str) -> str:
    # cerca il blocco waSticky e sostituisce il contenuto interno con SVG
    # Manteniamo id/class/href ecc., sostituiamo solo i figli interni
    pattern = r'(<a[^>]*id="waSticky"[^>]*>)([\s\S]*?)(</a>)'
    m = re.search(pattern, html, flags=re.IGNORECASE)
    if not m:
        return html

    start, _, end = m.group(1), m.group(2), m.group(3)
    new_inner = f'\n    <span class="wa-fab__icon" aria-hidden="true">{WA_SVG}</span>\n'
    return html[:m.start()] + start + new_inner + end + html[m.end():]

def process_html_file(p: Path):
    backup(p)
    html = p.read_text(encoding="utf-8")
    html2 = replace_fab_inner(html)
    p.write_text(html2, encoding="utf-8")

def main():
    # HTML: index + tutte le pagine in /case
    for f in FILES:
        if f.exists():
            process_html_file(f)

    if CASE_DIR.exists():
        for f in CASE_DIR.glob("*.html"):
            process_html_file(f)

    # CSS
    if CSS.exists():
        backup(CSS)
        css = CSS.read_text(encoding="utf-8")
        CSS.write_text(ensure_css(css), encoding="utf-8")

    print("✅ WhatsApp sticky aggiornato: SVG premium + cerchio icon-only (home + schede).")
    print("➡️ Test: python3 -m http.server 8000  →  http://localhost:8000")

if __name__ == "__main__":
    main()
