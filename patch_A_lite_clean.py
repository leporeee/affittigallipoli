#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch A Lite Clean — Salento Stay
Focus: ordine, chiarezza, zero caos.

- Rimuove filtri duplicati (mantiene una barra mini: Ospiti + Zona + Reset + contatore)
- Elimina link/testo "WhatsApp" fantasma nelle card
- Rende card cliccabile (overlay link) senza cambiare la struttura
- Filtro immediato + empty state (0 risultati)
- Barra filtri sticky SOTTILE (solo in sezione case)
- Aggiunge CSS/JS in modo idempotente (non duplica blocchi)
- Crea backup .bak-<timestamp>

Run: python3 patch_A_lite_clean.py
"""

import re
from pathlib import Path
from datetime import datetime

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
ROOT = Path(".").resolve()

INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
JS = ROOT / "script.js"

MARK = "PATCH_A_LITE_CLEAN_V1"


def backup(p: Path):
    if p.exists():
        p.with_suffix(p.suffix + f".bak-{STAMP}").write_text(
            p.read_text(encoding="utf-8", errors="ignore"),
            encoding="utf-8",
        )


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def write(p: Path, s: str):
    p.write_text(s, encoding="utf-8")


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def ensure_rel_img_paths(html: str) -> str:
    html = re.sub(r'src="/img/', 'src="img/', html, flags=re.I)
    html = re.sub(r'href="/img/', 'href="img/', html, flags=re.I)
    return html


def add_lazy_imgs(html: str) -> str:
    def repl(m):
        tag = m.group(0)
        if "loading=" in tag:
            return tag
        return tag.replace("<img", '<img loading="lazy" decoding="async"', 1)

    return re.sub(r"<img\b[^>]*>", repl, html, flags=re.I)


def remove_duplicate_filter_bars(html: str) -> str:
    """
    Rimuove:
    - blocchi Premium precedenti (se presenti)
    - eventuali duplicazioni di search/sort bar (id filtersBar o commenti)
    Tenendo solo la mini-bar che inseriamo noi.
    """
    # vecchi marker/blocks
    html = re.sub(r'<!--\s*PREMIUM_UX_A:FILTERS\s*-->[\s\S]*?<!--\s*END\s*PREMIUM_UX_A:FILTERS\s*-->\s*', '', html, flags=re.I)
    html = re.sub(r'<!--\s*PREMIUM_UX_A:FILTERS\s*-->[\s\S]*?</div>\s*', '', html, flags=re.I)
    html = re.sub(r'<div[^>]*\bid="filtersBar"[^>]*>[\s\S]*?</div>\s*', '', html, flags=re.I)

    # Rimuovi una seconda toolbar "Case consigliate" duplicata (pattern generico)
    # Se esistono due select di ordinamento ravvicinate, elimina quella più in alto (greedy safe)
    html = re.sub(r'(<select[^>]*id="sort"[^>]*>[\s\S]*?</select>)[\s\S]*?(<select[^>]*id="sort"[^>]*>[\s\S]*?</select>)',
                  r'\2', html, flags=re.I)

    return html


def inject_single_clean_bar(html: str) -> str:
    if f"<!-- {MARK}:BAR -->" in html:
        return html

    bar = f"""
<!-- {MARK}:BAR -->
<div class="caseBar" id="caseBar">
  <div class="caseBar__row">
    <div class="caseBar__group">
      <div class="caseBar__label">Ospiti</div>
      <div class="chips" id="cbGuests">
        <button class="chip is-active" type="button" data-guest="all">Tutti</button>
        <button class="chip" type="button" data-guest="2-4">2–4</button>
        <button class="chip" type="button" data-guest="4-8">4–8</button>
        <button class="chip" type="button" data-guest="8-12">8–12</button>
        <button class="chip" type="button" data-guest="12+">12+</button>
      </div>
    </div>

    <div class="caseBar__group">
      <div class="caseBar__label">Zona</div>
      <div class="chips" id="cbZones">
        <button class="chip is-active" type="button" data-zone="all">Tutte</button>
      </div>
    </div>

    <div class="caseBar__right">
      <button class="btn btn--ghost" id="cbReset" type="button">Reset</button>
    </div>
  </div>

  <div class="caseBar__meta">
    <span id="cbCount" class="results">Mostro tutte le case</span>
    <span id="cbEmpty" class="empty" style="display:none;">Nessuna casa per questi filtri. Prova un’altra fascia o una zona diversa.</span>
  </div>
</div>
"""

    # inserisci sopra la griglia cards
    m = re.search(r'(<div[^>]*class="[^"]*\bcards\b[^"]*"[^>]*>)', html, flags=re.I)
    if m:
        return html[:m.start()] + bar + "\n" + html[m.start():]
    return html + "\n" + bar


def remove_whatsapp_ghost(html: str) -> str:
    # elimina qualsiasi link o span col solo testo "WhatsApp" dentro le card
    html = re.sub(r'(<article\b[^>]*class="[^"]*\bcard\b[^"]*"[\s\S]*?</article>)',
                  lambda m: re.sub(r'<a\b[^>]*>\s*WhatsApp\s*</a>', '', m.group(1), flags=re.I),
                  html, flags=re.I)
    html = re.sub(r'(<article\b[^>]*class="[^"]*\bcard\b[^"]*"[\s\S]*?</article>)',
                  lambda m: re.sub(r'<span\b[^>]*>\s*WhatsApp\s*</span>', '', m.group(1), flags=re.I),
                  html, flags=re.I)
    return html


def ensure_card_data_and_clickable(html: str) -> str:
    pattern = r'(<article\b[^>]*class="[^"]*\bcard\b[^"]*"[\s\S]*?</article>)'

    def patch_card(card: str) -> str:
        # data-guests
        if "data-guests=" not in card:
            mg = re.search(r"👥\s*([0-9]{1,2})\s*osp", card, flags=re.I)
            if not mg:
                mg = re.search(r"\b([0-9]{1,2})\s*ospiti\b", card, flags=re.I)
            if mg:
                g = mg.group(1)
                card = re.sub(
                    r'(<article\b[^>]*class="[^"]*\bcard\b[^"]*"[^>]*)',
                    rf'\1 data-guests="{g}"',
                    card, flags=re.I, count=1,
                )

        # data-zone
        if "data-zone=" not in card:
            mz = re.search(r"📍\s*([A-Za-zÀ-ÿ0-9'’\-\s]{2,40})", card)
            if mz:
                z = normalize_spaces(mz.group(1))
                card = re.sub(
                    r'(<article\b[^>]*class="[^"]*\bcard\b[^"]*"[^>]*)',
                    rf'\1 data-zone="{z}"',
                    card, flags=re.I, count=1,
                )

        # overlay link card-clickable
        if "cardLinkOverlay" in card:
            return card

        mh = re.search(r'<a\b[^>]*href="([^"]*case/[^"]+)"', card, flags=re.I)
        if not mh:
            return card
        href = mh.group(1)

        # inserisci overlay link subito dopo l'apertura dell'article
        card = re.sub(
            r'(<article\b[^>]*>)',
            rf'\1<a class="cardLinkOverlay" href="{href}" aria-label="Apri dettagli"></a>',
            card, flags=re.I, count=1
        )

        return card

    return re.sub(pattern, lambda m: patch_card(m.group(1)), html, flags=re.I)


def inject_css(css: str) -> str:
    if f"/* === {MARK}:CSS === */" in css:
        return css

    block = f"""
/* === {MARK}:CSS === */

/* Sticky sottile solo in sezione case */
.caseBar {{
  position: sticky;
  top: 70px;
  z-index: 12;
  margin: 10px 0 16px;
  padding: 12px;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: rgba(11,13,18,.62);
  backdrop-filter: blur(6px);
  box-shadow: 0 16px 40px rgba(0,0,0,.30);
}}
.caseBar__row {{
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: end;
}}
.caseBar__group {{ display:flex; flex-direction:column; gap:8px; }}
.caseBar__label {{ font-size:12px; color: var(--muted); }}
.caseBar__right {{ margin-left: auto; display:flex; align-items:end; }}
.caseBar__meta {{
  margin-top: 10px;
  display:flex;
  gap: 12px;
  align-items:center;
  flex-wrap: wrap;
}}
.results {{ color: var(--muted); font-size: 13px; }}
.empty {{ color: var(--muted); font-size: 13px; opacity: .95; }}

/* Chips */
.chips {{ display:flex; gap:8px; flex-wrap:wrap; }}
.chip {{
  padding: 9px 11px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,.04);
  color: var(--text);
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: transform .12s ease, background .12s ease, border-color .12s ease;
}}
.chip:hover {{ transform: translateY(-1px); background: rgba(255,255,255,.07); }}
.chip.is-active {{
  background: rgba(69,102,255,.18);
  border-color: rgba(69,102,255,.45);
}}

/* Card clickable overlay */
.card {{ position: relative; }}
.cardLinkOverlay {{
  position:absolute;
  inset:0;
  z-index:2;
  border-radius: inherit;
}}
/* lascia i bottoni cliccabili sopra overlay */
.card a.btn, .card button, .card .btn {{
  position: relative;
  z-index: 3;
}}
"""
    return css + "\n" + block


def remove_old_blocks_js(js: str) -> str:
    js = re.sub(r"// === PATCH_A_LITE_CLEAN_V1:JS ===[\s\S]*?// === END PATCH_A_LITE_CLEAN_V1:JS ===\s*", "", js, flags=re.I)
    return js


def inject_js(js: str) -> str:
    if f"// === {MARK}:JS ===" in js:
        return js

    js = remove_old_blocks_js(js)

    block = f"""
// === {MARK}:JS ===
(function(){{
  function cards(){{ return Array.from(document.querySelectorAll(".card")); }}
  function norm(s){{ return (s||"").toString().trim(); }}

  function parseRange(v){{
    if(!v || v==="all") return {{min:0,max:99,label:"Tutti"}};
    if(v==="12+") return {{min:12,max:99,label:"12+"}};
    var m = v.match(/(\\d+)\\s*[-–]\\s*(\\d+)/);
    if(m) return {{min:parseInt(m[1],10),max:parseInt(m[2],10),label:v}};
    return {{min:0,max:99,label:"Tutti"}};
  }}

  function uniqueZones(){{
    var set = new Set();
    cards().forEach(function(c){{
      var z = norm(c.dataset.zone);
      if(z) set.add(z);
    }});
    return Array.from(set).sort(function(a,b){{ return a.localeCompare(b); }});
  }}

  function populateZones(){{
    var wrap = document.getElementById("cbZones");
    if(!wrap) return;
    wrap.querySelectorAll('[data-zone]:not([data-zone="all"])').forEach(function(n){{ n.remove(); }});
    uniqueZones().forEach(function(z){{
      var b = document.createElement("button");
      b.type="button";
      b.className="chip";
      b.dataset.zone=z;
      b.textContent=z;
      wrap.appendChild(b);
    }});
  }}

  function setActive(containerId, attr, value){{
    var wrap = document.getElementById(containerId);
    if(!wrap) return;
    wrap.querySelectorAll(".chip").forEach(function(b){{
      b.classList.toggle("is-active", b.dataset[attr] === value);
    }});
  }}

  function apply(state){{
    var guest = state.guest || "all";
    var zone  = state.zone  || "all";
    var r = parseRange(guest);

    var visible = 0;
    cards().forEach(function(c){{
      var g = parseInt(c.dataset.guests || "0", 10);
      var z = norm(c.dataset.zone);
      var okG = (guest==="all") ? true : (g>=r.min && g<=r.max);
      var okZ = (zone==="all")  ? true : (z.toLowerCase() === norm(zone).toLowerCase());
      var ok = okG && okZ;
      c.style.display = ok ? "" : "none";
      if(ok) visible++;
    }});

    var cnt = document.getElementById("cbCount");
    var empty = document.getElementById("cbEmpty");
    if(cnt){{
      var parts = [];
      parts.push("Mostro " + visible + " case");
      if(zone!=="all") parts.push("Zona: " + zone);
      if(guest!=="all") parts.push("Ospiti: " + guest);
      cnt.textContent = parts.join(" • ");
    }}
    if(empty) empty.style.display = (visible===0) ? "" : "none";

    setActive("cbGuests","guest",guest);
    setActive("cbZones","zone",zone);
  }}

  document.addEventListener("click", function(e){{
    var chip = e.target.closest(".chip");
    if(!chip) return;

    var gActive = document.querySelector("#cbGuests .chip.is-active")?.dataset.guest || "all";
    var zActive = document.querySelector("#cbZones .chip.is-active")?.dataset.zone || "all";

    var next = {{ guest: gActive, zone: zActive }};
    if(chip.dataset.guest) next.guest = chip.dataset.guest;
    if(chip.dataset.zone)  next.zone  = chip.dataset.zone;

    apply(next);
  }});

  document.addEventListener("DOMContentLoaded", function(){{
    populateZones();
    apply({{guest:"all", zone:"all"}});
    var reset = document.getElementById("cbReset");
    if(reset) reset.addEventListener("click", function(){{ apply({{guest:"all", zone:"all"}}); }});
  }});
}})();
// === END {MARK}:JS ===
"""
    return js.rstrip() + "\n\n" + block + "\n"


def main():
    if not INDEX.exists():
        print("❌ Non trovo index.html. Esegui nella cartella del sito.")
        return

    backup(INDEX)
    html = read(INDEX)
    html = ensure_rel_img_paths(html)
    html = add_lazy_imgs(html)
    html = remove_duplicate_filter_bars(html)
    html = remove_whatsapp_ghost(html)
    html = ensure_card_data_and_clickable(html)
    html = inject_single_clean_bar(html)
    write(INDEX, html)

    if CSS.exists():
        backup(CSS)
        css = read(CSS)
        css = inject_css(css)
        write(CSS, css)

    if JS.exists():
        backup(JS)
        js = read(JS)
        js = inject_js(js)
        write(JS, js)

    print("✅ Patch A Lite Clean applicata.")
    print("➡️ Test: python3 -m http.server 8000  →  http://localhost:8000")
    print("➡️ Se ti piace: git add -A && git commit -m \"Clean UX\" && git push")


if __name__ == "__main__":
    main()
