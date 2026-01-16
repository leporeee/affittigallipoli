from pathlib import Path
import shutil
import re

PROPS = [
  {"name":"ATENA", "slug":"atena", "loc":"Baia Verde", "guests":9, "hint":"🛏️ 3 camere + 2 bagni", "img":"ATENA.jpg", "pdf":"ATENA.pdf"},
  {"name":"BAIA VERDE", "slug":"baia-verde", "loc":"Baia Verde", "guests":6, "hint":"🚗 Parcheggio privato custodito", "img":"BAIA-VERDE.jpg", "pdf":"BAIA-VERDE.pdf"},
  {"name":"VILLA AZZURRA", "slug":"villa-azzurra", "loc":"Baia Verde", "guests":10, "hint":"🌿 Giardino attrezzato + terrazzo", "img":"VILLA-AZZURRA.jpg", "pdf":"VILLA-AZZURRA.pdf"},
  {"name":"ZEUS", "slug":"zeus", "loc":"Baia Verde", "guests":7, "hint":"🚿 Doccia esterna + giardino recintato", "img":"VILLETTA-ZEUS.jpg", "pdf":"VILLETTA-ZEUS.pdf"},
  {"name":"SIRENA", "slug":"sirena", "loc":"Baia Verde", "guests":5, "hint":"🌿 Indipendente con giardino retrostante", "img":"SIRENA.jpg", "pdf":"SIRENA.pdf"},
  {"name":"ARMONIA", "slug":"armonia", "loc":"Gallipoli", "guests":5, "hint":"🌅 Balcone vista mare", "img":"ARMONIA.jpg", "pdf":"ARMONIA.pdf"},
  {"name":"VILLETTA GEMMA C", "slug":"villetta-gemma-c", "loc":"Gallipoli", "guests":4, "hint":"🆕 Nuova costruzione + doccia esterna", "img":"VILLETTA-GEMMA-C.jpg", "pdf":"VILLETTA-GEMMA-C.pdf"},
  {"name":"BAIACRI", "slug":"baiacri", "loc":"Gallipoli", "guests":6, "hint":"🌅 Balcone vista mare (tende parasole)", "img":"BAIACRI.jpg", "pdf":"BAIACRI.pdf"},
  {"name":"MIRAMARE", "slug":"miramare", "loc":"Gallipoli", "guests":8, "hint":"🛁 2 bagni + 3 camere", "img":"MIRAMARE.jpg", "pdf":"MIRAMARE.pdf"},
  {"name":"LA PERLA", "slug":"la-perla", "loc":"Gallipoli", "guests":10, "hint":"❄️ Clima in ogni ambiente", "img":"LA-PERLA.jpg", "pdf":"LA-PERLA.pdf"},
  {"name":"MONDONUOVO", "slug":"mondonuovo", "loc":"Gallipoli", "guests":7, "hint":"🏊 Piscina nel residence", "img":"MONDONUOVO.jpg", "pdf":"MONDONUOVO.pdf"},
]

ROOT = Path(".").resolve()
INBOX = ROOT / "INBOX"
IMG_DIR = ROOT / "img" / "case"
PDF_DIR = ROOT / "pdf" / "case"
CASE_DIR = ROOT / "case"

def must_exist(p: Path):
  if not p.exists():
    raise SystemExit(f"File mancante: {p}")

def write_case_page(prop):
  slug = prop["slug"]
  img = f"/img/case/{slug}.jpg"
  pdf = f"/pdf/case/{slug}.pdf"
  title = prop["name"]
  loc = prop["loc"]
  guests = prop["guests"]
  hint = prop["hint"]

  wa_msg = f"Ciao! Vorrei disponibilità per {title} ({loc}) per {guests} ospiti."
  wa_url = "https://wa.me/393292272939?text=" + re.sub(r" ", "%20", wa_msg)

  html = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} | Affitti Gallipoli</title>
  <link rel="stylesheet" href="/styles.css" />
</head>
<body>
  <header class="topbar">
    <div class="container topbar__inner">
      <a class="brand" href="/">
        <div class="brand__logo">AG</div>
        <div>
          <div class="brand__name">Affitti Gallipoli</div>
          <div class="brand__tagline">Case vacanza</div>
        </div>
      </a>
      <a class="btn btn--ghost" href="/">← Home</a>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <div class="hero__grid">
        <div>
          <div class="pill">📍 {loc} &nbsp;•&nbsp; 👥 {guests} ospiti</div>
          <h1>{title}</h1>
          <p class="lead">{hint}</p>
          <div class="hero__cta">
            <a class="btn btn--primary" href="{pdf}" target="_blank" rel="noopener">Scarica scheda PDF</a>
            <a class="btn btn--secondary" href="{wa_url}" target="_blank" rel="noopener">Chiedi disponibilità</a>
          </div>
        </div>
        <div class="hero__media">
          <img src="{img}" alt="{title}">
        </div>
      </div>
    </section>
  </main>
</body>
</html>
"""
  (CASE_DIR / f"{slug}.html").write_text(html, encoding="utf-8")

def build_cards_html():
  cards = []
  for p in PROPS:
    slug = p["slug"]
    cards.append(f"""
      <article class="card">
        <img src="/img/case/{slug}.jpg" alt="{p['name']}">
        <div class="card__body">
          <h3>{p['name']}</h3>
          <ul class="meta">
            <li>📍 {p['loc']}</li>
            <li>👥 {p['guests']} ospiti</li>
            <li>{p['hint']}</li>
          </ul>
          <div class="card__foot">
            <a class="link" href="/case/{slug}.html">Vedi dettagli →</a>
          </div>
        </div>
      </article>
    """.strip())
  return '<div class="cards">\n' + "\n".join(cards) + "\n</div>\n"

def patch_index():
  idx = ROOT / "index.html"
  html = idx.read_text(encoding="utf-8")

  start = "<!-- AUTO_CARDS_START -->"
  end = "<!-- AUTO_CARDS_END -->"
  cards = build_cards_html()

  if start in html and end in html:
    before = html.split(start)[0]
    after = html.split(end)[1]
    new_html = before + start + "\n" + cards + end + after
    idx.write_text(new_html, encoding="utf-8")
    return

  # fallback: replace first <div class="cards">...</div>
  new_html = re.sub(r"<div class=\"cards\">.*?</div>\s*", cards, html, count=1, flags=re.S)
  idx.write_text(new_html, encoding="utf-8")

def main():
  if not INBOX.exists():
    raise SystemExit("Crea la cartella INBOX e mettici dentro JPG+PDF.")

  IMG_DIR.mkdir(parents=True, exist_ok=True)
  PDF_DIR.mkdir(parents=True, exist_ok=True)
  CASE_DIR.mkdir(parents=True, exist_ok=True)

  for p in PROPS:
    src_img = INBOX / p["img"]
    src_pdf = INBOX / p["pdf"]
    must_exist(src_img)
    must_exist(src_pdf)

    dst_img = IMG_DIR / f"{p['slug']}.jpg"
    dst_pdf = PDF_DIR / f"{p['slug']}.pdf"

    shutil.copy2(src_img, dst_img)
    shutil.copy2(src_pdf, dst_pdf)

    write_case_page(p)

  patch_index()
  print("OK: create pagine + copiati asset + aggiornata home.")

if __name__ == "__main__":
  main()
