import re
from pathlib import Path
from datetime import datetime

ROOT = Path(".")
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
JS = ROOT / "script.js"
CASE_DIR = ROOT / "case"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

def backup(p: Path):
    if p.exists():
        p.with_suffix(p.suffix + f".bak-{STAMP}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

WA_SVG = '''
<svg class="wa-fab__svg" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
  <path d="M16.02 3C9.39 3 4 8.2 4 14.6c0 2.23.8 4.3 2.14 5.97L5 29l8.65-1.88c1.26.35 2.58.54 3.95.54 6.63 0 12.02-5.2 12.02-11.6C29.62 8.2 22.65 3 16.02 3zm0 2.26c5.3 0 9.6 4.03 9.6 9.0s-4.3 9-9.6 9c-1.22 0-2.4-.2-3.5-.6l-.68-.24-5.14 1.12 1.33-4.84-.45-.6c-1.07-1.42-1.64-3.08-1.64-4.84 0-4.97 4.3-9 9.6-9zm-4.3 5.3c-.22 0-.58.08-.88.4-.3.32-1.15 1.1-1.15 2.67 0 1.57 1.18 3.1 1.35 3.3.17.2 2.32 3.62 5.72 4.93 2.82 1.1 3.4.88 4.02.82.62-.06 2.02-.8 2.3-1.57.28-.78.28-1.44.2-1.57-.08-.13-.3-.2-.62-.35-.32-.15-2.02-1-2.33-1.12-.3-.12-.53-.2-.75.12-.22.32-.87 1.12-1.07 1.35-.2.23-.4.26-.72.1-.32-.15-1.33-.48-2.53-1.53-.93-.82-1.56-1.83-1.74-2.15-.18-.32-.02-.5.13-.66.14-.16.32-.4.48-.6.16-.2.2-.35.32-.58.12-.23.06-.43-.02-.6-.08-.17-.73-1.9-1.03-2.6-.26-.6-.55-.62-.75-.62h-.63z"/>
</svg>
'''.strip()

def ensure_fab(html: str) -> str:
    # se già c'è waSticky, non reinserire
    if 'id="waSticky"' in html:
        return html

    fab = f"""
  <!-- WhatsApp Sticky FAB -->
  <a id="waSticky" class="wa-fab" href="#" target="_blank" rel="noopener" aria-label="Contattaci su WhatsApp">
    <span class="wa-fab__icon" aria-hidden="true">{WA_SVG}</span>
  </a>
"""
    return re.sub(r"</body>", fab + "\n</body>", html, flags=re.IGNORECASE, count=1)

def force_svg_inside_fab(html: str) -> str:
    # se esiste waSticky, sostituisce il contenuto interno con svg (evita emoji/scritta)
    pat = r'(<a[^>]*id="waSticky"[^>]*>)([\s\S]*?)(</a>)'
    m = re.search(pat, html, flags=re.IGNORECASE)
    if not m:
        return html
    start, end = m.group(1), m.group(3)
    inner = f'\n    <span class="wa-fab__icon" aria-hidden="true">{WA_SVG}</span>\n'
    return html[:m.start()] + start + inner + end + html[m.end():]

def strip_old_hide_rules(css: str) -> str:
    # rimuove blocchi vecchi che nascondono la wa-fab (display:none !important) per evitare conflitti
    css = re.sub(r'\.wa-fab\s*\{[^}]*display\s*:\s*none\s*!important;?[^}]*\}\s*', '', css, flags=re.IGNORECASE)
    # rimuove anche eventuali vecchi blocchi "solo mobile" che impostavano display inline-flex dentro media query
    css = re.sub(r'@media\s*\(max-width:\s*520px\)\s*\{\s*\.wa-fab\s*\{[^}]*display\s*:\s*inline-flex\s*!important;?[^}]*\}\s*\}\s*',
                 '', css, flags=re.IGNORECASE)
    return css

def ensure_css(css: str) -> str:
    if "/* === WA FAB REFINED === */" in css:
        return css
    css = strip_old_hide_rules(css)

    block = r"""
/* === WA FAB REFINED === */
/* Desktop: appare dopo scroll (JS) con animazione pulita */
.wa-fab{
  position: fixed;
  right: calc(18px + env(safe-area-inset-right, 0px));
  bottom: calc(18px + env(safe-area-inset-bottom, 0px));
  z-index: 9999;

  width: 54px;
  height: 54px;
  padding: 0 !important;
  border-radius: 999px !important;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  background: rgba(37,211,102,.10);
  border: 1px solid rgba(37,211,102,.28);
  backdrop-filter: blur(10px);

  box-shadow: 0 22px 60px rgba(0,0,0,.45);
  transform: translateY(10px);
  opacity: 0;
  pointer-events: none;

  transition: opacity .18s ease, transform .18s ease, box-shadow .18s ease, background .18s ease;
}

.wa-fab.is-visible{
  opacity: 1;
  transform: none;
  pointer-events: auto;
}

.wa-fab:hover{
  transform: translateY(-2px);
  background: rgba(37,211,102,.14);
  box-shadow: 0 28px 80px rgba(0,0,0,.55);
}

.wa-fab:focus-visible{
  outline: 3px solid rgba(69,102,255,.55);
  outline-offset: 3px;
}

.wa-fab__icon{
  width: 42px;
  height: 42px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: rgba(37,211,102,.20);
  border: 1px solid rgba(37,211,102,.30);
}

.wa-fab__svg{
  width: 22px;
  height: 22px;
  fill: rgba(233,238,251,.96);
}

/* Mobile: sempre visibile e un filo più grande */
@media (max-width: 520px){
  .wa-fab{
    width: 58px;
    height: 58px;
    opacity: 1;
    transform: none;
    pointer-events: auto;
    right: calc(14px + env(safe-area-inset-right, 0px));
    bottom: calc(14px + env(safe-area-inset-bottom, 0px));
  }
  .wa-fab__icon{ width: 46px; height: 46px; }
  .wa-fab__svg{ width: 24px; height: 24px; }
}

@media (prefers-reduced-motion: reduce){
  .wa-fab{ transition: none !important; }
}
"""
    return css + "\n" + block

def ensure_js(js: str) -> str:
    if "// === WA FAB DESKTOP VISIBILITY ===" in js:
        return js

    block = r"""
// === WA FAB DESKTOP VISIBILITY ===
(function(){
  const fab = document.getElementById("waSticky");
  if(!fab) return;

  // Mostralo su desktop dopo un piccolo scroll (più rapido = più facile vederlo)
  const DESKTOP_SCROLL_SHOW = 60;

  function update(){
    if(window.innerWidth <= 520){
      fab.classList.add("is-visible");
      return;
    }
    fab.classList.toggle("is-visible", window.scrollY > DESKTOP_SCROLL_SHOW);
  }

  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
  update();

  // Nascondilo quando il footer entra in vista (non copre i link)
  const footer = document.querySelector("footer");
  if(footer && "IntersectionObserver" in window){
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(e=>{
        if(window.innerWidth > 520){
          const show = !e.isIntersecting && window.scrollY > DESKTOP_SCROLL_SHOW;
          fab.classList.toggle("is-visible", show);
        }
      });
    }, { threshold: 0.10 });
    io.observe(footer);
  }
})();
"""
    return js + "\n" + block

def process_html_file(p: Path):
    backup(p)
    html = p.read_text(encoding="utf-8")
    html = ensure_fab(html)
    html = force_svg_inside_fab(html)
    p.write_text(html, encoding="utf-8")

def main():
    # HTML: index + pagine case
    if INDEX.exists():
        process_html_file(INDEX)
    if CASE_DIR.exists():
        for f in CASE_DIR.glob("*.html"):
            process_html_file(f)

    # CSS
    if CSS.exists():
        backup(CSS)
        css = CSS.read_text(encoding="utf-8")
        CSS.write_text(ensure_css(css), encoding="utf-8")

    # JS
    if JS.exists():
        backup(JS)
