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

def strip_text_span(html: str) -> str:
    # rimuove eventuali <span class="wa-fab__text">WhatsApp</span>
    html = re.sub(r'<span[^>]*class="[^"]*wa-fab__text[^"]*"[^>]*>[\s\S]*?</span>', '', html, flags=re.I)
    return html

def force_icon_only_inside_sticky(html: str) -> str:
    # se dentro #waSticky c'è qualsiasi testo "WhatsApp", lo elimina
    pat = r'(<a[^>]*id="waSticky"[^>]*>)([\s\S]*?)(</a>)'
    m = re.search(pat, html, flags=re.I)
    if not m:
        return html

    start, inner, end = m.group(1), m.group(2), m.group(3)
    # tieni SOLO lo span icona + svg (se esiste)
    icon = re.search(r'(<span[^>]*class="[^"]*wa-fab__icon[^"]*"[\s\S]*?</span>)', inner, flags=re.I)
    new_inner = icon.group(1) if icon else inner
    # pulizia extra: rimuovi eventuali "WhatsApp" testuali residui
    new_inner = re.sub(r'WhatsApp', '', new_inner, flags=re.I)

    return html[:m.start()] + start + new_inner + end + html[m.end():]

def ensure_css_kill_text(css: str) -> str:
    if "/* === FAB TEXT KILL (iOS) === */" in css:
        return css
    block = r"""
/* === FAB TEXT KILL (iOS) === */
/* Qualsiasi testo dentro il FAB non deve MAI comparire */
#waSticky, .wa-fab{
  width: 56px !important;
  height: 56px !important;
  padding: 0 !important;
  border-radius: 999px !important;
  overflow: hidden !important;
  white-space: nowrap !important;
  font-size: 0 !important; /* uccide testo “fantasma” */
}
#waSticky .wa-fab__text, .wa-fab .wa-fab__text{
  display: none !important;
  visibility: hidden !important;
  position: absolute !important;
  left: -9999px !important;
}

/* rimette dimensione al logo */
#waSticky .wa-fab__svg, .wa-fab .wa-fab__svg{
  font-size: initial !important;
}
@media (max-width: 520px){
  #waSticky, .wa-fab{
    width: 60px !important;
    height: 60px !important;
  }
}
"""
    return css + "\n\n" + block

def process_html(p: Path):
    backup(p)
    html = p.read_text(encoding="utf-8")
    html = strip_text_span(html)
    html = force_icon_only_inside_sticky(html)
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
        CSS.write_text(ensure_css_kill_text(css), encoding="utf-8")

    print("✅ FATTO: testo WhatsApp rimosso dal FAB + CSS anti-bug iOS applicato.")

if __name__ == "__main__":
    main()
