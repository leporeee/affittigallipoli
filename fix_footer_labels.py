from pathlib import Path
import re

ROOT = Path(".").resolve()

def patch_index():
    p = ROOT / "index.html"
    if not p.exists():
        raise SystemExit("index.html non trovato")

    html = p.read_text(encoding="utf-8", errors="ignore")

    # Sostituisce solo il blocco footer__links con due voci pulite
    def repl(m):
        return (
            '<div class="footer__links">\n'
            '      <a href="/privacy.html">Privacy</a>\n'
            '      <a href="#form">Contatti</a>\n'
            '    </div>'
        )

    html2, n = re.subn(
        r'<div class="footer__links">.*?</div>',
        repl,
        html,
        count=1,
        flags=re.S
    )

    if n == 0:
        raise SystemExit('Non trovo <div class="footer__links"> in index.html')

    p.write_text(html2, encoding="utf-8")
    print("OK index.html footer links")

def patch_privacy():
    p = ROOT / "privacy.html"
    if not p.exists():
        raise SystemExit("privacy.html non trovato")

    html = p.read_text(encoding="utf-8", errors="ignore")

    # Qui "Contatti" deve essere WhatsApp con id waFooter (per script.js)
    html = re.sub(
        r'<div class="footer__links">.*?</div>',
        '<div class="footer__links">\n'
        '        <a href="/privacy.html">Privacy</a>\n'
        '        <a id="waFooter" href="#">Contatti</a>\n'
        '      </div>',
        html,
        count=1,
        flags=re.S
    )

    p.write_text(html, encoding="utf-8")
    print("OK privacy.html footer links")

if __name__ == "__main__":
    patch_index()
    patch_privacy()
    print("Fatto.")

