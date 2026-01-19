#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path
from datetime import datetime

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

ROOT = Path(".").resolve()
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
JS = ROOT / "script.js"

MARK = "CLEAN_FILTERS_V3"

def backup(p: Path):
    if p.exists():
        p.with_suffix(p.suffix + f".bak-{STAMP}").write_text(
            p.read_text(encoding="utf-8", errors="ignore"),
            encoding="utf-8"
        )

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def write(p: Path, s: str):
    p.write_text(s, encoding="utf-8")

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

def strip_old_insertions(html: str) -> str:
    # Rimuove vecchie barre inserite (anche duplicate) di patch precedenti
    patterns = [
        r'<!--\s*PATCH_A_LITE_CLEAN_V1:BAR\s*-->[\s\S]*?(?=(<!--\s*PATCH_A_LITE_CLEAN_V1:BAR\s*-->|<div[^>]*class="[^"]*\bcards\b))',
        r'<!--\s*PATCH_A_LITE_CLEAN_V1:MINIFILTERS\s*-->[\s\S]*?(?=(<!--\s*PATCH_A_LITE_CLEAN_V1:MINIFILTERS\s*-->|<div[^>]*class="[^"]*\bcards\b))',
        r'<!--\s*LITE_CLEAN_A:MINIFILTERS\s*-->[\s\S]*?(?=(<!--\s*LITE_CLEAN_A:MINIFILTERS\s*-->|<div[^>]*class="[^"]*\bcards\b))',
        r'<!--\s*LITE_CLEAN_A_V2:MINIFILTERS\s*-->[\s\S]*?(?=(<!--\s*LITE_CLEAN_A_V2:MINIFILTERS\s*-->|<div[^>]*class="[^"]*\bcards\b))',
        r'<!--\s*' + MARK + r':BAR\s*-->[\s\S]*?(?=(<!--\s*' + MARK + r':BAR\s*-->|<div[^>]*class="[^"]*\bcards\b))',
        r'<div[^>]*\bid="caseBar"[^>]*>[\s\S]*?(?=<div[^>]*class="[^"]*\bcards\b)',
    ]
    out = html
    for pat in patterns:
        out = re.sub(pat, "", out, flags=re.I)
    return out

def inject_single_bar(html: str) -> str:
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
      <div class="caseBar__label">Ordina</div>
      <select class="caseBar__select" id="cbSort" aria-label="Ordina">
        <option value="default">Consigliate</option>
        <option value="guestsAsc">Ospiti ↑</option>
        <option value="guestsDesc">Ospiti ↓</option>
        <option value="zoneAZ">Zona A–Z</option>
      </select>
      <button class="btn btn--ghost" id="cbReset" type="button">Reset</button>
    </div>
  </div>

  <div class="caseBar__meta">
    <span id="cbCount" class="results">Mostro tutte le case</span>
    <span id="cbEmpty" class="empty" style="display:none;">Nessuna casa per questi filtri. Prova un’altra fascia o una zona diversa.</span>
  </div>
</div>
"""

    m = re.search(r'(<div[^>]*class="[^"]*\bcards\b[^"]*"[^>]*>)', html, flags=re.I)
    if m:
        return html[:m.start()] + bar + "\n" + html[m.start():]
    return html + "\n" + bar

def css_strip(css: str) -> str:
    # Rimuove blocchi vecchi se presenti (messi sempre in fondo)
    css = re.sub(r"/\*\s*=== PATCH_A_LITE_CLEAN_V1:CSS ===\s*\*/[\s\S]*$", "", css, flags=re.I)
    css = re.sub(r"/\*\s*=== LITE_CLEAN_A:CSS ===\s*\*/[\s\S]*$", "", css, flags=re.I)
    css = re.sub(r"/\*\s*=== LITE_CLEAN_A_V2:CSS ===\s*\*/[\s\S]*$", "", css, flags=re.I)
    css = re.sub(r"/\*\s*=== " + re.escape(MARK) + r":CSS ===\s*\*/[\s\S]*$", "", css, flags=re.I)
    return css

def css_inject(css: str) -> str:
    if f"/* === {MARK}:CSS === */" in css:
        return css

    block = f"""
/* === {MARK}:CSS === */

/* Barra filtri UNICA: sottile e pulita */
.caseBar {{
  position: sticky;
  top: 70px;
  z-index: 12;
  margin: 10px 0 16px;
  padding: 10px 12px;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: rgba(11,13,18,.62);
  backdrop-filter: blur(6px);
  box-shadow: 0 14px 34px rgba(0,0,0,.28);
}}

.caseBar__row {{
  display:flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: end;
}}

.caseBar__group {{ display:flex; flex-direction:column; gap:8px; }}
.caseBar__label {{ font-size:12px; color: var(--muted); }}

.caseBar__right {{
  margin-left: auto;
  display:flex;
  gap:10px;
  align-items:end;
  flex-wrap: wrap;
}}

.caseBar__select {{
  border-radius: 14px;
  border: 1px solid var(--line);
  background: rgba(11,13,18,.55);
  color: var(--text);
  padding: 9px 10px;
  font: inherit;
}}

.caseBar__meta {{
  margin-top: 8px;
  display:flex;
  gap: 12px;
  align-items:center;
  flex-wrap: wrap;
}}

.results, .empty {{ color: var(--muted); font-size: 13px; }}

/* Chips */
.chips {{ display:flex; gap:8px; flex-wrap:wrap; }}
.chip {{
  padding: 8px 11px;
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

/* Nascondi la barra legacy "Case consigliate" (verrà marcata via JS) */
.legacyHide {{ display:none !important; }}
"""
    return css.rstrip() + "\n\n" + block + "\n"

def js_strip(js: str) -> str:
    js = re.sub(r"// === PATCH_A_LITE_CLEAN_V1:JS ===[\s\S]*$", "", js, flags=re.I)
    js = re.sub(r"// === LITE_CLEAN_A:JS ===[\s\S]*$", "", js, flags=re.I)
    js = re.sub(r"// === LITE_CLEAN_A_V2:JS ===[\s\S]*$", "", js, flags=re.I)
    js = re.sub(r"// === " + re.escape(MARK) + r":JS ===[\s\S]*$", "", js, flags=re.I)
    return js

def js_inject(js: str) -> str:
    if f"// === {MARK}:JS ===" in js:
        return js

    block = f"""
// === {MARK}:JS ===
(function(){{
  function norm(s){{ return (s||"").toString().trim(); }}
  function cardsWrap(){{ return document.querySelector(".cards"); }}
  function cards(){{ return Array.from(document.querySelectorAll(".card")); }}

  function parseGuestsFromCard(card){{
    var d = card.dataset.guests;
    if(d) return parseInt(d,10);
    var t = card.textContent || "";
    var m = t.match(/(\\d{{1,2}})\\s*osp/i) || t.match(/(\\d{{1,2}})\\s*ospiti/i);
    return m ? parseInt(m[1],10) : 0;
  }}

  function parseZoneFromCard(card){{
    var d = card.dataset.zone;
    if(d) return norm(d);
    var t = card.textContent || "";
    // prova a prendere Baia Verde / Gallipoli ecc. se presenti
    var zones = ["Baia Verde","Gallipoli","Lido San Giovanni","Centro","Rivabella","Alezio"];
    for(var i=0;i<zones.length;i++){{ if(t.toLowerCase().includes(zones[i].toLowerCase())) return zones[i]; }}
    // fallback: cerca dopo 📍
    var m = t.match(/📍\\s*([^\\n•]+)/);
    return m ? norm(m[1]) : "";
  }}

  function uniqueZones(){{
    var set = new Set();
    cards().forEach(function(c){{
      var z = parseZoneFromCard(c);
      if(z) set.add(z);
      c.dataset.zone = z; // normalizza
      c.dataset.guests = String(parseGuestsFromCard(c)); // normalizza
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

  function parseRange(v){{
    if(!v || v==="all") return {{min:0,max:99}};
    if(v==="12+") return {{min:12,max:99}};
    var m = v.match(/(\\d+)\\s*[-–]\\s*(\\d+)/);
    if(m) return {{min:parseInt(m[1],10), max:parseInt(m[2],10)}};
    return {{min:0,max:99}};
  }}

  function setActive(containerId, attr, value){{
    var wrap = document.getElementById(containerId);
    if(!wrap) return;
    wrap.querySelectorAll(".chip").forEach(function(b){{
      b.classList.toggle("is-active", b.dataset[attr] === value);
    }});
  }}

  function applyFilters(state){{
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

  function setupSort(){{
    var sel = document.getElementById("cbSort");
    var wrap = cardsWrap();
    if(!sel || !wrap) return;

    // salva ordine originale
    var original = Array.from(wrap.children);
    original.forEach(function(el, i){{ el.dataset.orig = String(i); }});

    function sortNow(mode){{
      var items = Array.from(wrap.children);
      function guests(el){{ return parseInt(el.dataset.guests||"0",10); }}
      function zone(el){{ return norm(el.dataset.zone).toLowerCase(); }}
      function orig(el){{ return parseInt(el.dataset.orig||"0",10); }}

      if(mode==="default") items.sort(function(a,b){{ return orig(a)-orig(b); }});
      if(mode==="guestsAsc") items.sort(function(a,b){{ return guests(a)-guests(b) || orig(a)-orig(b); }});
      if(mode==="guestsDesc") items.sort(function(a,b){{ return guests(b)-guests(a) || orig(a)-orig(b); }});
      if(mode==="zoneAZ") items.sort(function(a,b){{ return zone(a).localeCompare(zone(b)) || orig(a)-orig(b); }});

      items.forEach(function(el){{ wrap.appendChild(el); }});
    }}

    sel.addEventListener("change", function(){{ sortNow(sel.value); }});
    sortNow("default");
  }}

  function makeCardsClickable(){{
    document.addEventListener("click", function(e){{
      var card = e.target.closest(".card");
      if(!card) return;
      if(e.target.closest("a,button,select,textarea,input")) return;

      var link = card.querySelector('a[href*="case/"]');
      if(link) window.location.href = link.getAttribute("href");
    }});
  }}

  function hideLegacyToolbar(){{
    // Cerca l'heading "Case consigliate" e nasconde il box che lo contiene
    var headings = Array.from(document.querySelectorAll("h1,h2,h3,h4,p,strong"));
    var h = headings.find(function(x){{ return norm(x.textContent).toLowerCase() === "case consigliate"; }});
    if(!h) return;

    var box = h.closest("div");
    // sali finché trovi un box che contiene input+select (toolbar)
    for(var i=0;i<4 && box; i++) {{
      var hasInput = !!box.querySelector('input[placeholder*="Cerca"]');
      var hasSelect = !!box.querySelector("select");
      var hasCards = box.querySelectorAll(".card").length > 0;
      if(hasInput && hasSelect && !hasCards) break;
      box = box.parentElement;
    }}
    if(box) box.classList.add("legacyHide");
  }}

  function removeDuplicateBars(){{
    var bars = Array.from(document.querySelectorAll("#caseBar"));
    if(bars.length <= 1) return;
    // tieni l'ultimo (di solito è quello vicino alle cards)
    for(var i=0;i<bars.length-1;i++) bars[i].remove();
  }}

  document.addEventListener("DOMContentLoaded", function(){{
    hideLegacyToolbar();
    removeDuplicateBars();
    populateZones();
    applyFilters({{guest:"all", zone:"all"}});
    setupSort();
    makeCardsClickable();

    var reset = document.getElementById("cbReset");
    if(reset) reset.addEventListener("click", function(){{ applyFilters({{guest:"all", zone:"all"}}); }});
  }});

  document.addEventListener("click", function(e){{
    var chip = e.target.closest(".chip");
    if(!chip) return;

    var gActive = document.querySelector("#cbGuests .chip.is-active")?.dataset.guest || "all";
    var zActive = document.querySelector("#cbZones .chip.is-active")?.dataset.zone || "all";

    var next = {{ guest: gActive, zone: zActive }};
    if(chip.dataset.guest) next.guest = chip.dataset.guest;
    if(chip.dataset.zone)  next.zone  = chip.dataset.zone;

    applyFilters(next);
  }});
}})();
"""
    return js.rstrip() + "\n\n" + block + "\n"

def main():
    if not INDEX.exists():
        print("❌ Non trovo index.html. Esegui nella cartella del sito.")
        return

    # index
    backup(INDEX)
    html = read(INDEX)
    html = ensure_rel_img_paths(html)
    html = add_lazy_imgs(html)
    html = strip_old_insertions(html)
    html = inject_single_bar(html)
    write(INDEX, html)

    # css
    if CSS.exists():
        backup(CSS)
        css = read(CSS)
        css = css_strip(css)
        css = css_inject(css)
        write(CSS, css)

    # js
    if JS.exists():
        backup(JS)
        js = read(JS)
        js = js_strip(js)
        js = js_inject(js)
        write(JS, js)

    print("✅ Fix completato: barra unica + niente duplicati + legacy toolbar nascosta.")
    print("➡️ Test: python3 -m http.server 8000  →  http://localhost:8000")

if __name__ == "__main__":
    main()
