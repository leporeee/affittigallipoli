import re
from pathlib import Path
from datetime import datetime

ROOT = Path(".")
INDEX = ROOT / "index.html"
CASE_DIR = ROOT / "case"
CSS = ROOT / "styles.css"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

def backup(p: Path):
    if p.exists():
        p.with_suffix(p.suffix + f".bak-{STAMP}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

# WhatsApp logo SVG (Font Awesome style) - super riconoscibile e centrato
WA_SVG = r'''
<svg class="wa-fab__svg" viewBox="0 0 448 512" aria-hidden="true" focusable="false">
  <path d="M380.9 97.1C339 55.1 283.2 32 223.9 32 100.1 32-.6 132.3 0 256c.2 45.1 12 89.2 34.3 128.2L0 480l101.7-32.4c37.2 20.3 79.1 31 122.2 31h.1c123.7 0 224-100.3 224-224 0-59.3-23.1-115-65.1-157.5zM223.9 438.7h-.1c-38.3 0-75.9-10.3-108.7-29.8l-7.8-4.6-60.3 19.2 19.6-58.8-5.1-8.1C39.7 322.6 28.2 289.5 28 256 27.5 148.4 115.6 60.3 223.9 60.3c51.8 0 100.5 20.2 137.1 56.8 36.6 36.6 56.8 85.3 56.8 137.1 0 108.3-88.1 196.5-193.9 196.5zm107.3-147.1c-5.9-3-34.8-17.1-40.2-19.1-5.4-2-9.3-3-13.2 3-3.9 5.9-15.1 19.1-18.5 23-3.4 3.9-6.8 4.4-12.7 1.5-5.9-3-24.9-9.2-47.5-29.4-17.6-15.7-29.5-35.1-33-41-3.4-5.9-.4-9.1 2.6-12 2.7-2.7 5.9-6.8 8.8-10.2 3-3.4 3.9-5.9 5.9-9.8 2-3.9 1-7.3-.5-10.2-1.5-3-13.2-31.8-18.1-43.6-4.7-11.3-9.4-9.8-13.2-10-3.4-.2-7.3-.2-11.2-.2-3.9 0-10.2 1.5-15.6 7.3-5.4 5.9-20.5 20-20.5 48.8 0 28.8 21 56.6 23.9 60.5 3 3.9 41.4 63.2 100.3 88.6 14 6 24.9 9.6 33.4 12.3 14 4.4 26.8 3.8 36.9 2.3 11.3-1.7 34.8-14.2 39.7-27.9 4.9-13.7 4.9-25.4 3.4-27.9-1.5-2.5-5.4-3.9-11.3-6.9z"/>
</svg>
'''.strip()

def replace_fab_inner(html: str) -> str:
    # sostituisce l'interno del link waSticky con lo span+svg premium
    pat = r'(<a[^>]*id="waSticky"[^>]*>)([\s\S]*?)(</a>)'
    m = re.search(pat, html, flags=re.IGNORECASE)
    if not m:
        return html
    start, end = m.group(1), m.group(3)
    inner = f'\n  <span class="wa-fab__icon" aria-hidden="true">{WA_SVG}</span>\n'
    return html[:m.start()] + start + inner + end + html[m.end():]

def ensure_css_override(css: str) -> str:
    if "/* === WA FAB PREMIUM LOGO === */" in css:
        return css
    block = r"""
/* === WA FAB PREMIUM LOGO === */
/* Un solo cerchio pulito, logo perfetto */
.wa-fab{
  background: rgba(37,211,102,.95) !important;
  border: none !important;
  box-shadow: 0 22px 60px rgba(0,0,0,.45) !important;
}
.wa-fab:hover{
  background: rgba(37,211,102,1) !important;
  box-shadow: 0 28px 80px rgba(0,0,0,.55) !important;
}
.wa-fab__icon{
  background: transparent !important;
  border: none !important;
  width: 100% !important;
  height: 100% !important;
  display: grid !important;
  place-items: center !important;
}
.wa-fab__svg{
  width: 26px !important;
  height: 26px !important;
  fill: #ffffff !important;
  display: block !important;
}

/* Mobile: un filo più grande */
@media (max-width: 520px){
  .wa-fab__svg{ width: 28px !important; height: 28px !important; }
}
"""
    return css + "\n" + block

def process_html(p: Path):
    backup(p)
    html = p.read_text(encoding="utf-8")
    html = replace_fab_inner(html)
    p.write_text(html, encoding="utf-8")

def main():
    if INDEX.exists():
        process_html(INDEX)

    if CASE_DIR.exists():
        for f in CASE_DIR.glob("*.html"):
            process_html(f)

    if CSS.exists():
        backup(CSS)
        css = CSS.read_text(encoding="utf-8")
        CSS.write_text(ensure_css_override(css), encoding="utf-8")

    print("✅ WhatsApp FAB: logo premium (SVG vero) + cerchio pulito (niente doppio bordo).")

if __name__ == "__main__":
    main()
