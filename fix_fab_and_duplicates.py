import re
from pathlib import Path
from datetime import datetime

ROOT = Path(".")
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
CASE_DIR = ROOT / "case"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

def backup(p: Path):
    if p.exists():
        p.with_suffix(p.suffix + f".bak-{STAMP}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

def ensure_visible_class(html: str) -> str:
    # rende sempre visibile il FAB senza dipendere da JS: aggiunge is-visible alla classe
    def repl(m):
        tag = m.group(0)
        # sostituisce class="wa-fab" o class="wa-fab ..."
        if 'class="' in tag:
            tag = re.sub(r'class="([^"]*)"', lambda mm: f'class="{mm.group(1)}{" is-visible" if "is-visible" not in mm.group(1) else ""}"', tag)
        return tag

    return re.sub(r'<a[^>]*id="waSticky"[^>]*>', repl, html, flags=re.IGNORECASE)

def ensure_css_has_is_visible(css: str) -> str:
    # nel dubbio, aggiunge regola is-visible se manca
    if re.search(r'\.wa-fab\.is-visible', css):
        return css
    return css + "\n\n/* Force visible state */\n.wa-fab.is-visible{opacity:1;transform:none;pointer-events:auto;}\n"

def remove_duplicate_pdf_buttons_in_case(html: str) -> str:
    """
    Se c'è action-bar, rimuove bottoni duplicati fuori da action-bar:
    - Scarica scheda PDF
    - Apri scheda (PDF)
    - Chiedi disponibilità
    - Chiedi disponibilità su WhatsApp
    """
    m = re.search(r'(<div class="action-bar"[\s\S]*?</div>)', html, flags=re.IGNORECASE)
    if not m:
        return html

    action_bar = m.group(1)
    placeholder = "__ACTION_BAR__PLACEHOLDER__"
    temp = html.replace(action_bar, placeholder, 1)

    # Rimuovi anchor/button con quei testi (fuori dall'action bar)
    texts = [
        r"Scarica\s+scheda\s+PDF",
        r"Apri\s+scheda\s*\(PDF\)",
        r"Chiedi\s+disponibilit[aà]\s+su\s+WhatsApp",
        r"Chiedi\s+disponibilit[aà]"
    ]

    for t in texts:
        # <a ...> TESTO </a>
        temp = re.sub(rf'<a\b[^>]*>\s*{t}\s*</a>', "", temp, flags=re.IGNORECASE)
        # <button ...> TESTO </button> (nel caso)
        temp = re.sub(rf'<button\b[^>]*>\s*{t}\s*</button>', "", temp, flags=re.IGNORECASE)

    # pulisci div vuoti rimasti (un paio di volte)
    for _ in range(3):
        temp = re.sub(r'<div[^>]*>\s*</div>', "", temp, flags=re.IGNORECASE)

    # rimetti action bar
    temp = temp.replace(placeholder, action_bar, 1)
    return temp

def process_html_file(p: Path, is_case: bool):
    backup(p)
    html = p.read_text(encoding="utf-8")
    html = ensure_visible_class(html)
    if is_case:
        html = remove_duplicate_pdf_buttons_in_case(html)
    p.write_text(html, encoding="utf-8")

def main():
    # HTML
    if INDEX.exists():
        process_html_file(INDEX, is_case=False)

    if CASE_DIR.exists():
        for f in CASE_DIR.glob("*.html"):
            process_html_file(f, is_case=True)

    # CSS (solo aggiunta is-visible se manca)
    if CSS.exists():
        backup(CSS)
        css = CSS.read_text(encoding="utf-8")
        CSS.write_text(ensure_css_has_is_visible(css), encoding="utf-8")

    print("✅ FIX OK: FAB sempre visibile (desktop+mobile) + rimozione bottoni PDF/WA duplicati nelle schede.")
    print("➡️ Test: python3 -m http.server 8000  →  http://localhost:8000")

if __name__ == "__main__":
    main()
