from pathlib import Path
import re

ROOT = Path(".").resolve()
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
PRIVACY = ROOT / "privacy.html"
FILTER_JS = ROOT / "filter.js"

PRIVACY_HTML = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Privacy Policy | Salento Stay</title>
  <link rel="stylesheet" href="/styles.css" />
</head>
<body>
  <header class="topbar">
    <div class="container topbar__inner">
      <a class="brand" href="/">
        <div class="brand__logo">SS</div>
        <div>
          <div class="brand__name">Salento Stay</div>
          <div class="brand__tagline">Case vacanza</div>
        </div>
      </a>
      <a class="btn btn--ghost" href="/">← Home</a>
    </div>
  </header>

  <main class="container section">
    <div class="section__head">
      <h2>Privacy Policy</h2>
      <p class="muted">Ultimo aggiornamento: 2026-01-17</p>
    </div>

    <div class="form" style="max-width: 860px;">
      <p>Questo sito è gestito da <strong>Salento Stay</strong> ed ha finalità esclusivamente informative.</p>
      <p>Il sito non raccoglie dati personali tramite moduli o sistemi di registrazione.</p>
      <p>I contatti avvengono tramite WhatsApp (servizio esterno gestito da Meta Platforms Inc.).</p>
      <p>Il provider di hosting (Vercel) può raccogliere dati tecnici per motivi di sicurezza e funzionamento.</p>
      <p>Questo sito non utilizza cookie di profilazione.</p>
    </div>
  </main>

  <footer class="footer">
    <div class="container footer__inner">
      <div class="muted">© <span id="year"></span> Salento Stay</div>
      <div class="footer__links">
        <a href="/privacy.html">Privacy Policy</a>
        <a id="waFooter" href="#">WhatsApp</a>
      </div>
    </div>
  </footer>

  <script src="/script.js"></script>
  <script src="/filter.js"></script>
</body>
</html>
"""

FILTER_JS_TEXT = r"""document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("propertyGrid");
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll("article"));

  function parseGuestsFromText(card) {
    const txt = card.textContent || "";
    const m = txt.match(/👥\s*(\d+)\s*ospiti/i);
    return m ? parseInt(m[1], 10) : null;
  }

  function getGuests(card) {
    const v = card.getAttribute("data-guests");
    if (v) return parseInt(v, 10);
    return parseGuestsFromText(card);
  }

  function getDetailsHref(card) {
    const a = card.querySelector("a.link[href]");
    if (a) return a.getAttribute("href");
    const any = card.querySelector("a[href]");
    return any ? any.getAttribute("href") : null;
  }

  // Foto cliccabile (stesso link di "Vedi dettagli" se esiste e non è #anchor)
  cards.forEach(card => {
    const img = card.querySelector("img");
    const href = getDetailsHref(card);
    if (!img || !href) return;
    if (href.startsWith("#")) return;

    img.style.cursor = "pointer";
    img.addEventListener("click", () => window.location.href = href);
  });

  // UI filtro (se già esiste), altrimenti la creiamo sopra la griglia
  let filterBar = document.getElementById("guestsFilterBar");
  if (!filterBar) {
    filterBar = document.createElement("div");
    filterBar.className = "filterbar";
    filterBar.id = "guestsFilterBar";
    filterBar.innerHTML = `
      <button class="btn btn--ghost" data-filter="all">Tutti</button>
      <button class="btn btn--ghost" data-filter="1-4">1–4 posti</button>
      <button class="btn btn--ghost" data-filter="5-6">5–6 posti</button>
      <button class="btn btn--ghost" data-filter="7-8">7–8 posti</button>
      <button class="btn btn--ghost" data-filter="9+">9+ posti</button>
    `;
    grid.parentElement.insertBefore(filterBar, grid);
  }

  function matchesRule(g, rule) {
    if (!g) return rule === "all";
    if (rule === "all") return True;
    if (rule === "1-4") return g >= 1 && g <= 4;
    if (rule === "5-6") return g >= 5 && g <= 6;
    if (rule === "7-8") return g >= 7 && g <= 8;
    if (rule === "9+") return g >= 9;
    return true;
  }

  function applyFilter(rule) {
    cards.forEach(card => {
      const g = getGuests(card);
      let show = true;
      if (rule === "all") show = true;
      else if (rule === "1-4") show = g >= 1 && g <= 4;
      else if (rule === "5-6") show = g >= 5 && g <= 6;
      else if (rule === "7-8") show = g >= 7 && g <= 8;
      else if (rule === "9+") show = g >= 9;

      card.classList.toggle("is-hidden", !show);
    });
  }

  filterBar.querySelectorAll("[data-filter]").forEach(btn => {
    btn.addEventListener("click", () => applyFilter(btn.dataset.filter));
  });
});
"""

CSS_APPEND = """
/* --- Guests filter bar + animazioni filtro --- */
.filterbar{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  margin: 10px 0 18px;
}

article.card, article.property-card, #propertyGrid article{
  transition: opacity .22s ease, transform .22s ease;
  will-change: opacity, transform;
}

.is-hidden{
  opacity: 0;
  transform: translateY(6px) scale(.99);
  pointer-events: none;
  height: 0 !important;
  margin: 0 !important;
}
"""

def ensure_privacy():
  PRIVACY.write_text(PRIVACY_HTML, encoding="utf-8")

def patch_footer_privacy(index_html: str) -> str:
  if "/privacy.html" in index_html:
    return index_html
  # Prova a inserirlo nel blocco footer__links
  m = re.search(r'(<div\s+class="footer__links"\s*>)', index_html)
  if not m:
    return index_html
  insert = m.group(1) + '\n        <a href="/privacy.html">Privacy Policy</a>'
  return index_html.replace(m.group(1), insert, 1)

def ensure_filter_js_include(index_html: str) -> str:
  if 'src="/filter.js"' in index_html or "src='/filter.js'" in index_html:
    return index_html
  # Inserisci prima di </body>
  return re.sub(r"</body>", '  <script src="/filter.js"></script>\n</body>', index_html, count=1, flags=re.I)

def add_data_guests(index_html: str) -> str:
  # Aggiunge data-guests="X" a ogni <article ...> leggendo "👥 X ospiti" nel contenuto
  def repl(match):
    open_tag = match.group(1)
    inner = match.group(2)

    gm = re.search(r"👥\s*(\d+)\s*ospiti", inner, flags=re.I)
    if not gm:
      return match.group(0)

    guests = gm.group(1)

    if re.search(r'\bdata-guests\s*=\s*"', open_tag):
      open_tag2 = re.sub(r'\bdata-guests\s*=\s*"\d+"', f'data-guests="{guests}"', open_tag)
    else:
      open_tag2 = open_tag[:-1] + f' data-guests="{guests}">'

    return open_tag2 + inner + "</article>"

  return re.sub(r"(<article\b[^>]*>)(.*?)</article>", repl, index_html, flags=re.S | re.I)

def ensure_filter_js_file():
  FILTER_JS.write_text(FILTER_JS_TEXT, encoding="utf-8")

def append_css():
  css = CSS.read_text(encoding="utf-8")
  if "Guests filter bar" in css or ".filterbar" in css:
    return
  CSS.write_text(css + "\n" + CSS_APPEND, encoding="utf-8")

def main():
  if not INDEX.exists():
    raise SystemExit("index.html non trovato nella cartella corrente.")
  if not CSS.exists():
    raise SystemExit("styles.css non trovato nella cartella corrente.")

  ensure_privacy()
  ensure_filter_js_file()
  append_css()

  html = INDEX.read_text(encoding="utf-8")
  html = add_data_guests(html)
  html = patch_footer_privacy(html)
  html = ensure_filter_js_include(html)
  INDEX.write_text(html, encoding="utf-8")

  print("OK: privacy.html creato, index patchato (privacy link + data-guests + filter.js), styles.css aggiornato, filter.js creato.")

if __name__ == "__main__":
  main()
