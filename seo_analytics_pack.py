#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
import re
from urllib.parse import urljoin

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
ROOT = Path(".").resolve()

INDEX = ROOT / "index.html"
CASE_DIR = ROOT / "case"

SITE_URL_DEFAULT = "https://affittigallipoli.vercel.app/"  # cambia se metti dominio tuo
BRAND = "Salento Stay"

# 1) Metti qui il tuo GA4 ID quando lo crei (es: G-ABC123XYZ).
# Se lo lasci vuoto, lo script NON inserisce GA.
GA4_ID = ""  # <-- incolla qui il tuo G-XXXX quando ce l'hai

def backup(p: Path):
    if p.exists():
        b = p.with_suffix(p.suffix + f".bak-{STAMP}")
        b.write_text(p.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        return b
    return None

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def write(p: Path, s: str):
    p.write_text(s, encoding="utf-8")

def guess_site_url() -> str:
    # prova a leggere un canonical già presente, altrimenti usa default
    if INDEX.exists():
        html = read(INDEX)
        m = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, flags=re.I)
        if m:
            u = m.group(1).strip()
            if u.endswith("/"):
                return u
            return u + "/"
    return SITE_URL_DEFAULT

def ensure_head(html: str) -> str:
    if "<head" not in html.lower():
        raise SystemExit("❌ Non trovo <head> nel file (HTML strano).")
    return html

def upsert_tag(html: str, pattern: str, replacement: str) -> str:
    # se esiste pattern, sostituisci, altrimenti inserisci replacement prima di </head>
    if re.search(pattern, html, flags=re.I):
        return re.sub(pattern, replacement, html, flags=re.I)
    return re.sub(r"</head>", replacement + "\n</head>", html, flags=re.I)

def strip_existing_marked_block(html: str, start_mark: str, end_mark: str) -> str:
    # rimuove blocchi precedenti
    return re.sub(re.escape(start_mark) + r"[\s\S]*?" + re.escape(end_mark), "", html)

def title_for_page(path: Path) -> str:
    if path.name == "index.html":
        return f"{BRAND} • Case e appartamenti a Gallipoli (prenota su WhatsApp)"
    # case page
    slug = path.stem.replace("-", " ").title()
    return f"{slug} • {BRAND} Gallipoli"

def description_for_page(path: Path) -> str:
    if path.name == "index.html":
        return "Vetrina di case e appartamenti a Gallipoli e dintorni. Scrivici su WhatsApp con date e numero ospiti: rispondiamo velocemente con le migliori opzioni."
    slug = path.stem.replace("-", " ").title()
    return f"Dettagli e documenti per {slug}. Contattaci su WhatsApp per disponibilità, date e preventivo."

def og_image_for_page(path: Path, html: str) -> str:
    # usa la prima immagine trovata nella pagina come og:image (se è locale)
    m = re.search(r'<img[^>]+src="([^"]+)"', html, flags=re.I)
    if m:
        src = m.group(1).strip()
        if src.startswith("http"):
            return src
        # normalizza a URL assoluto
        return src.lstrip("/")
    # fallback: nessuna immagine
    return "img/case/atena.jpg"

def build_ga_snippet(ga_id: str) -> str:
    return f"""
<!-- GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}', {{ anonymize_ip: true }});
</script>
<!-- /GA4 -->
""".strip()

def build_jsonld_home(site_url: str) -> str:
    # schema semplice (non “sparato”)
    return f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LodgingBusiness",
  "name": "{BRAND}",
  "url": "{site_url}",
  "areaServed": "Gallipoli, Salento, Puglia",
  "address": {{
    "@type": "PostalAddress",
    "addressLocality": "Gallipoli",
    "addressRegion": "LE",
    "addressCountry": "IT"
  }}
}}
</script>
""".strip()

def build_jsonld_case(site_url: str, page_url: str, name: str) -> str:
    return f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LodgingBusiness",
  "name": "{name}",
  "url": "{page_url}",
  "isPartOf": {{
    "@type": "LodgingBusiness",
    "name": "{BRAND}",
    "url": "{site_url}"
  }},
  "areaServed": "Gallipoli, Salento, Puglia"
}}
</script>
""".strip()

def patch_page(path: Path, site_url: str):
    html = read(path)
    html = ensure_head(html)

    # ripulisci blocchi precedenti (se riesegui lo script)
    html = strip_existing_marked_block(html, "<!-- SEO_PACK:START -->", "<!-- SEO_PACK:END -->")

    page_url = urljoin(site_url, path.name) if path.name == "index.html" else urljoin(site_url, f"case/{path.name}")

    title = title_for_page(path)
    desc = description_for_page(path)
    og_img = og_image_for_page(path, html)

    canonical = page_url
    if canonical.endswith("index.html"):
        canonical = site_url

    # blocco unico ordinato
    seo_block = f"""
<!-- SEO_PACK:START -->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0d12">

<title>{title}</title>
<meta name="description" content="{desc}">

<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{urljoin(site_url, og_img)}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{urljoin(site_url, og_img)}">
<!-- SEO_PACK:END -->
""".strip()

    # Inserisci il blocco SEO subito prima di </head> (o lo aggiorna)
    html = re.sub(r"</head>", seo_block + "\n</head>", html, flags=re.I)

    # GA4 (solo se impostato)
    if GA4_ID.strip():
        ga = build_ga_snippet(GA4_ID.strip())
        # evita duplicati
        html = re.sub(r"<!-- GA4 -->[\s\S]*?<!-- /GA4 -->\s*", "", html, flags=re.I)
        html = re.sub(r"</head>", ga + "\n</head>", html, flags=re.I)

    # JSON-LD
    jsonld = build_jsonld_home(site_url) if path.name == "index.html" else build_jsonld_case(
        site_url, canonical, path.stem.replace("-", " ").title()
    )
    # evita duplicati jsonld
    html = re.sub(r"<script type=\"application/ld\+json\">[\s\S]*?</script>\s*", "", html, flags=re.I)
    html = re.sub(r"</head>", jsonld + "\n</head>", html, flags=re.I)

    write(path, html)

def write_robots(site_url: str):
    robots = f"""User-agent: *
Allow: /

Sitemap: {urljoin(site_url, "sitemap.xml")}
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")

def write_sitemap(site_url: str):
    urls = []
    # home
    urls.append(site_url)

    # case pages
    if CASE_DIR.exists():
        for p in sorted(CASE_DIR.glob("*.html")):
            urls.append(urljoin(site_url, f"case/{p.name}"))

    # privacy (se c'è)
    priv = ROOT / "privacy.html"
    if priv.exists():
        urls.append(urljoin(site_url, "privacy.html"))

    now = datetime.utcnow().strftime("%Y-%m-%d")

    items = "\n".join(
        [f"""  <url>
    <loc>{u}</loc>
    <lastmod>{now}</lastmod>
  </url>""" for u in urls]
    )

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

def main():
    if not INDEX.exists():
        raise SystemExit("❌ index.html non trovato. Esegui nella cartella del sito.")

    site_url = guess_site_url()
    # backup principali
    backup(INDEX)
    if CASE_DIR.exists():
        for p in CASE_DIR.glob("*.html"):
            backup(p)

    # patch home + schede
    patch_page(INDEX, site_url)
    if CASE_DIR.exists():
        for p in CASE_DIR.glob("*.html"):
            patch_page(p, site_url)

    # robots + sitemap
    write_robots(site_url)
    write_sitemap(site_url)

    print("✅ SEO pack applicato: meta/OG/canonical/jsonld + robots.txt + sitemap.xml")
    if not GA4_ID.strip():
        print("ℹ️ GA4 non inserito (GA4_ID vuoto). Quando hai il G-XXXX, incollalo in seo_analytics_pack.py e riesegui.")
    print("➡️ Test: python3 -m http.server 8000  →  http://localhost:8000")

if __name__ == "__main__":
    main()
