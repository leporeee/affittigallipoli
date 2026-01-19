import re
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

ROOT = Path(".")
CSS = ROOT / "styles.css"
HTML_FILES = [ROOT / "index.html"]
CASE_DIR = ROOT / "case"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

WHATSAPP_NUMBER = "393292272939"  # tuo numero (internazionale senza +)
DEFAULT_MSG = "Ciao! Vorrei informazioni e disponibilità per una casa a Gallipoli."

# SVG WhatsApp (premium, super riconoscibile)
WA_SVG = r'''
<svg class="wa-fab__svg" viewBox="0 0 448 512" aria-hidden="true" focusable="false">
  <path d="M380.9 97.1C339 55.1 283.2 32 223.9 32 100.1 32-.6 132.3 0 256c.2 45.1 12 89.2 34.3 128.2L0 480l101.7-32.4c37.2 20.3 79.1 31 122.2 31h.1c123.7 0 224-100.3 224-224 0-59.3-23.1-115-65.1-157.5zM223.9 438.7h-.1c-38.3 0-75.9-10.3-108.7-29.8l-7.8-4.6-60.3 19.2 19.6-58.8-5.1-8.1C39.7 322.6 28.2 289.5 28 256 27.5 148.4 115.6 60.3 223.9 60.3c51.8 0 100.5 20.2 137.1 56.8 36.6 36.6 56.8 85.3 56.8 137.1 0 108.3-88.1 196.5-193.9 196.5zm107.3-147.1c-5.9-3-34.8-17.1-40.2-19.1-5.4-2-9.3-3-13.2 3-3.9 5.9-15.1 19.1-18.5 23-3.4 3.9-6.8 4.4-12.7 1.5-5.9-3-24.9-9.2-47.5-29.4-17.6-15.7-29.5-35.1-33-41-3.4-5.9-.4-9.1 2.6-12 2.7-2.7 5.9-6.8 8.8-10.2 3-3.4 3.9-5.9 5.9-9.8 2-3.9 1-7.3-.5-10.2-1.5-3-13.2-31.8-18.1-43.6-4.7-11.3-9.4-9.8-13.2-10-3.4-.2-7.3-.2-11.2-.2-3.9 0-10.2 1.5-15.6 7.3-5.4 5.9-20.5 20-20.5 48.8 0 28.8 21 56.6 23.9 60.5 3 3.9 41.4 63.2 100.3 88.6 14 6 24.9 9.6 33.4 12.3 14 4.4 26.8 3.8 36.9 2.3 11.3-1.7 34.8-14.2 39.7-27.9 4.9-13.7 4.9-25.4 3.4-27.9-1.5-2.5-5.4-3.9-11.3-6.9z"/>
</svg>
'''.strip()

def backup(p: Path):
    if p.exists():
        p.with_suffix(p.suffix + f".bak-{STAMP}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

def wa_link(msg: str) -> str:
    # api.whatsapp.com a volte è più “affidabile” su mobile rispetto a wa.me
    return f"https://api.whatsapp.com/send?phone={WHATSAPP_NUMBER}&text={quote(msg)}"

def extract_title(html: str) -> str:
    # prova a prendere H1 come nome casa
    m = re.search(r"<h1[^>]*>\s*([^<]{2,80})\s*</h1>", html, flags=re.I)
    if m:
        t = re.sub(r"\s+", " ", m.group(1)).strip()
        return t
    return ""

def normalize_fab(html: str, msg: str) -> str:
    # 1) rimuove eventuali duplicati di waSticky (se presenti)
    blocks = list(re.finditer(r'<a[^>]*id="waSticky"[^>]*>[\s\S]*?</a>', html, flags=re.I))
    if len(blocks) > 1:
        # tieni il primo, elimina gli altri
        keep = blocks[0].group(0)
        for b in reversed(blocks[1:]):
            html = html[:b.start()] + "" + html[b.end():]
        # ricalcola primo (può essere cambiato)
        blocks = list(re.finditer(r'<a[^>]*id="waSticky"[^>]*>[\s\S]*?</a>', html, flags=re.I))

    if not blocks:
        return html  # se non c'è, non inventiamo nulla

    fab = blocks[0].group(0)

    # 2) forza href funzionante direttamente in HTML + target blank
    href = wa_link(msg)
    fab = re.sub(r'href="[^"]*"', f'href="{href}"', fab, flags=re.I)
    if 'href="' not in fab:
        fab = fab.replace("<a ", f'<a href="{href}" ', 1)

    if re.search(r'\btarget=', fab, flags=re.I) is None:
        fab = fab.replace("<a ", '<a target="_blank" rel="noopener" ', 1)

    # 3) forza classe wa-fab + is-visible
    def fix_class(m):
        cls = m.group(1)
        parts = cls.split()
        for need in ["wa-fab", "is-visible"]:
            if need not in parts:
                parts.append(need)
        return f'class="{" ".join(parts)}"'
    if re.search(r'class="[^"]*"', fab, flags=re.I):
        fab = re.sub(r'class="([^"]*)"', fix_class, fab, count=1, flags=re.I)
    else:
        fab = fab.replace("<a ", '<a class="wa-fab is-visible" ', 1)

    # 4) contenuto: SOLO icona + svg (niente testo visibile)
    inner = f'''
<span class="wa-fab__icon" aria-hidden="true">{WA_SVG}</span>
<span class="wa-fab__text" aria-hidden="true">WhatsApp</span>
'''.strip()
    fab = re.sub(r'(<a[^>]*id="waSticky"[^>]*>)[\s\S]*?(</a>)', rf'\1{inner}\2', fab, flags=re.I)

    # sostituisci nel documento
    html = html[:blocks[0].start()] + fab + html[blocks[0].end():]
    return html

def normalize_top_buttons(html: str, msg: str) -> str:
    href = wa_link(msg)
    for btn_id in ["waHero", "waFooter"]:
        # se esiste un anchor con quell'id, setta href (fallback HTML)
        html = re.sub(
            rf'(<a[^>]*id="{btn_id}"[^>]*)(>)',
            lambda m: (m.group(1) + ('' if re.search(r'href="', m.group(1), flags=re.I) else f' href="{href}"') + m.group(2)),
            html,
            flags=re.I
        )
        # se l'href c'è già, lo aggiorna
        html = re.sub(
            rf'(<a[^>]*id="{btn_id}"[^>]*href=")[^"]*(")',
            rf'\1{href}\2',
            html,
            flags=re.I
        )
    return html

def ensure_css(css: str) -> str:
    marker = "/* === WA FAB MOBILE FIX === */"
    if marker in css:
        return css

    block = f"""
{marker}
/* Cerchio vero (no pill), testo sempre nascosto */
.wa-fab {{
  position: fixed;
  right: 18px;
  bottom: calc(18px + env(safe-area-inset-bottom));
  width: 56px;
  height: 56px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(37,211,102,.98);
  border: none;
  z-index: 9999;
  box-shadow: 0 20px 60px rgba(0,0,0,.45);
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}}

.wa-fab__text {{
  display: none !important;
}}

.wa-fab__icon {{
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
}}

.wa-fab__svg {{
  width: 26px;
  height: 26px;
  fill: #fff;
  display: block;
}}

.wa-fab:hover {{
  transform: translateY(-1px);
  box-shadow: 0 28px 80px rgba(0,0,0,.55);
}}

.wa-fab:active {{
  transform: translateY(0px) scale(.98);
}}

@media (max-width: 520px) {{
  .wa-fab {{
    right: 16px;
    width: 60px;
    height: 60px;
  }}
  .wa-fab__svg {{
    width: 28px;
    height: 28px;
  }}
}}
"""
    return css + "\n\n" + block

def main():
    # lista file HTML
    if CASE_DIR.exists():
        HTML_FILES.extend(sorted(CASE_DIR.glob("*.html")))

    # CSS
    if CSS.exists():
        backup(CSS)
        css = CSS.read_text(encoding="utf-8")
        CSS.write_text(ensure_css(css), encoding="utf-8")

    # HTML
    for p in HTML_FILES:
        if not p.exists():
            continue
        backup(p)
        html = p.read_text(encoding="utf-8")

        title = extract_title(html)
        msg = DEFAULT_MSG if not title else f"Ciao! Vorrei disponibilità per {title}."
        html = normalize_top_buttons(html, DEFAULT_MSG)
        html = normalize_fab(html, msg)

        p.write_text(html, encoding="utf-8")

    print("✅ FATTO: su mobile sparisce la scritta, FAB è cerchio SVG premium e il link punta sempre al numero.")
    print("➡️ Ora fai commit & push.")

if __name__ == "__main__":
    main()
