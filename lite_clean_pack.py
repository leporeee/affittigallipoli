#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lite Clean Pack (A) — Salento Stay
Goal: remove redundancy + keep site simple and ordered.

Does:
- Removes hero smartbar (if present)
- Removes heavy filters bar (search/sort/sticky) and inserts mini filters (Guests + Zone + Reset) NON-sticky
- Removes duplicated "WhatsApp" text links inside cards (keeps the main WhatsApp button)
- Makes card image clickable to property page (if an href to /case/... exists)
- Adds minimal JS filter logic: guests range + zone
- Adds minimal CSS for mini filters

Creates timestamped .bak backups for modified files.
Run from project root:
  python3 lite_clean_pack.py
"""

import re
from pathlib import Path
from datetime import datetime

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

ROOT = Path(".").resolve()
INDEX = ROOT / "index.html"
CSS = ROOT / "styles.css"
JS = ROOT / "script.js"

MARK = "LITE_CLEAN_A"

def backup(p: Path):
    if p.exists():
        p.with_suffix(p.suffix + f".bak-{STAMP}").write_text(p.read_text(encoding="utf-8", errors="ignore"),
                                                            encoding="utf-8")

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def write(p: Path, s: str):
    p.write_text(s, encoding="utf-8")

def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def ensure_rel_img_paths(html: str) -> str:
    html = re.sub(r'src="/img/', 'src="img/', html, flags=re.I)
    html = re.sub(r'href="/img/', 'href="img/', html, flags=re.I)
    return html

def remove_hero_smartbar(html: str) -> str:
    # remove block if previously inserted
    html = re.sub(r'<!--\s*PREMIUM_UX_A:SMARTBAR\s*-->[\s\S]*?</div>\s*', '', html, flags=re.I)
    html = re.sub(r'<!--\s*PREMIUM_UX_A:SMARTBAR\s*-->[\s\S]*', '', html, flags=re.I)
    # remove any element with id=smartbar
    html = re.sub(r'<div[^>]*\bid="smartbar"[^>]*>[\s\S]*?</div>\s*', '', html, flags=re.I)
    return html

def remove_heavy_filters(html: str) -> str:
    # remove Premium filters block if present
    html = re.sub(r'<!--\s*PREMIUM_UX_A:FILTERS\s*-->[\s\S]*?</div>\s*</div>\s*', '', html, flags=re.I)
    html = re.sub(r'<!--\s*PREMIUM_UX_A:FILTERS\s*-->[\s\S]*?</div>\s*', '', html, flags=re.I)
    # remove any filters bar by id
    html = re.sub(r'<div[^>]*\bid="filtersBar"[^>]*>[\s\S]*?</div>\s*', '', html, flags=re.I)
    return html

def inject_mini_filters(html: str) -> str:
    if f"<!-- {MARK}:MINIFILTERS -->" in html:
        return html

    mini = f"""
<!-- {MARK}:MINIFILTERS -->
<div class="miniFilters" id="miniFilters">
  <div class="miniFilters__row">
    <div class="miniFilters__group">
      <div class="miniFilters__label">Ospiti</div>
      <div class="chips" id="mfGuests">
        <button class="chip is-active" type="button" data-guest="all">Tutti</button>
        <button class="chip" type="button" data-guest="2-4">2–4</button>
        <button class="chip" type="button" data-guest="4-8">4–8</button>
        <button class="chip" type="button" data-guest="8-12">8–12</button>
        <button class="chip" type="button" data-guest="12+">12+</button>
      </div>
    </div>

    <div class="miniFilters__group">
      <div class="miniFilters__label">Zona</div>
      <div class="chips" id="mfZones">
        <button class="chip is-active" type="button" data-zone="all">Tutte</button>
      </div>
    </div>

    <div class="miniFilters__group miniFilters__tools">
      <button class="btn btn--ghost" id="mfReset" type="button">Reset</button>
    </div>
  </div>

  <div class="miniFilters__meta">
    <span id="mfCount" class="results">Mostro tutte le case</span>
  </div>
</div>
"""

    # insert before the cards grid
    m = re.search(r'(<div[^>]*class="[^"]*\\bcards\\b[^"]*"[^>]*>)', html, flags=re.I)
    if m:
        return html[:m.start()] + mini + "\n" + html[m.start():]
    # fallback: append end
    return html + "\n" + mini

def add_lazy_imgs(html: str) -> str:
    def repl(m):
        tag = m.group(0)
        if "loading=" in tag:
            return tag
        return tag.replace("<img", '<img loading="lazy" decoding="async"', 1)
    return re.sub(r"<img\\b[^>]*>", repl, html, flags=re.I)

def make_cards_clickable_and_clean(html: str) -> str:
    # Remove duplicated text "WhatsApp" links that were appended (keep buttons like "Chiedi su WhatsApp")
    # Remove <a ...>WhatsApp</a> inside card__foot if present
    def clean_card(card: str) -> str:
        card = re.sub(r'<a[^>]*data-wa-card[^>]*>\\s*WhatsApp\\s*</a>', '', card, flags=re.I)
        card = re.sub(r'<a[^>]*>\\s*WhatsApp\\s*</a>', '', card, flags=re.I)

        # Add data attributes if missing (guests and zone from the small pills)
        if "data-guests=" not in card:
            mg = re.search(r"👥\\s*([0-9]{1,2})\\s*osp", card, flags=re.I)
            if not mg:
                mg = re.search(r"\\b([0-9]{1,2})\\s*ospiti\\b", card, flags=re.I)
            if mg:
                g = mg.group(1)
                card = re.sub(r'(<article\\b[^>]*class="[^"]*\\bcard\\b[^"]*"[^>]*)',
                              rf'\\1 data-guests="{g}"', card, flags=re.I, count=1)

        if "data-zone=" not in card:
            mz = re.search(r"📍\\s*([A-Za-zÀ-ÿ0-9'’\\-\\s]{2,40})", card)
            if mz:
                z = normalize_spaces(mz.group(1))
                card = re.sub(r'(<article\\b[^>]*class="[^"]*\\bcard\\b[^"]*"[^>]*)',
                              rf'\\1 data-zone="{z}"', card, flags=re.I, count=1)

        # Make first image clickable if there is a details link to /case/...
        if re.search(r"<a[^>]*>\\s*<img", card, flags=re.I):
            return card

        mh = re.search(r'<a[^>]*href="([^"]*case/[^"]+)"', card, flags=re.I)
        if not mh:
            return card
        href = mh.group(1)
        card = re.sub(r'(<img\\b[^>]*>)', rf'<a class="card__mediaLink" href="{href}">\\1</a>', card, flags=re.I, count=1)
        return card

    html = re.sub(r"(<article\\b[^>]*class=\\"card\\"[\\s\\S]*?</article>)",
                  lambda m: clean_card(m.group(1)),
                  html, flags=re.I)
    return html

def inject_css(css: str) -> str:
    if f"/* === {MARK}:CSS === */" in css:
        return css

    block = f"""
/* === {MARK}:CSS === */

/* Mini filters (NON sticky) */
.miniFilters{{
  margin: 6px 0 16px;
  padding: 12px;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: rgba(11,13,18,.55);
  backdrop-filter: blur(8px);
  box-shadow: var(--shadow);
}}
.miniFilters__row{{
  display:flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: end;
}}
.miniFilters__group{{ display:flex; flex-direction:column; gap:8px; }}
.miniFilters__label{{ font-size:12px; color: var(--muted); }}
.miniFilters__tools{{ margin-left: auto; }}
.miniFilters__meta{{ margin-top: 10px; display:flex; justify-content:space-between; align-items:center; }}
.results{{ color: var(--muted); font-size: 13px; }}

/* Chips base (se già esistono non cambia) */
.chips{{ display:flex; gap:8px; flex-wrap:wrap; }}
.chip{{
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
.chip:hover{{ transform: translateY(-1px); background: rgba(255,255,255,.07); }}
.chip.is-active{{
  background: rgba(69,102,255,.18);
  border-color: rgba(69,102,255,.45);
}}

/* Card media link */
.card__mediaLink img{{ transition: transform .25s ease; }}
.card:hover .card__mediaLink img{{ transform: scale(1.02); }}
"""
    return css + "\n" + block

def inject_js(js: str) -> str:
    # Remove old premium block if present to avoid chaos
    js = re.sub(r"// === PREMIUM_UX_A:JS ===[\\s\\S]*$", "", js, flags=re.I)

    if f"// === {MARK}:JS ===" in js:
        return js

    block = f"""
// === {MARK}:JS ===
(function(){{
  function getCards(){{ return Array.from(document.querySelectorAll(".card")); }}
  function norm(s){{ return (s||"").toString().trim(); }}

  function parseRange(v){{
    if(!v || v==="all") return {{min:0,max:99,label:"Tutti"}};
    if(v==="12+") return {{min:12,max:99,label:"12+"}};
    const m=v.match(/(\\d+)\\s*[-–]\\s*(\\d+)/);
    if(m) return {{min:parseInt(m[1],10),max:parseInt(m[2],10),label:v}};
    return {{min:0,max:99,label:"Tutti"}};
  }}

  function uniqueZones(){{
    const set=new Set();
    getCards().forEach(c=>{{
      const z=norm(c.dataset.zone);
      if(z) set.add(z);
    }});
    return Array.from(set).sort((a,b)=>a.localeCompare(b));
  }}

  function populateZones(){{
    const zones=uniqueZones();
    const wrap=document.getElementById("mfZones");
    if(!wrap) return;
    wrap.querySelectorAll('[data-zone]:not([data-zone="all"])').forEach(n=>n.remove());
    zones.forEach(z=>{{
      const b=document.createElement("button");
      b.type="button";
      b.className="chip";
      b.dataset.zone=z;
      b.textContent=z;
      wrap.appendChild(b);
    }});
  }}

  function setActive(container, attr, value){{
    if(!container) return;
    container.querySelectorAll(".chip").forEach(b=>{{
      const v=b.dataset[attr];
      b.classList.toggle("is-active", v===value);
    }});
  }}

  function applyFilters(state){{
    const guest=state.guest || "all";
    const zone=state.zone || "all";
    const r=parseRange(guest);

    let visible=0;
    getCards().forEach(c=>{{
      const g=parseInt(c.dataset.guests||"0",10);
      const z=norm(c.dataset.zone);
      const okG = guest==="all" ? true : (g>=r.min && g<=r.max);
      const okZ = zone==="all" ? true : (z.toLowerCase()===norm(zone).toLowerCase());
      const ok=okG && okZ;
      c.style.display = ok ? "" : "none";
      if(ok) visible++;
    }});

    const cnt=document.getElementById("mfCount");
    if(cnt){{
      const parts=[];
      parts.push("Mostro " + visible + " case");
      if(zone!=="all") parts.push("Zona: " + zone);
      if(guest!=="all") parts.push("Ospiti: " + guest);
      cnt.textContent = parts.join(" • ");
    }}

    setActive(document.getElementById("mfGuests"), "guest", guest);
    setActive(document.getElementById("mfZones"), "zone", zone);
  }}

  document.addEventListener("click", (e)=>{{
    const chip=e.target.closest(".chip");
    if(!chip) return;

    const gWrap=document.getElementById("mfGuests");
    const zWrap=document.getElementById("mfZones");

    const activeGuest = gWrap?.querySelector(".chip.is-active")?.dataset.guest || "all";
    const activeZone  = zWrap?.querySelector(".chip.is-active")?.dataset.zone || "all";

    const next={{guest: activeGuest, zone: activeZone}};
    if(chip.dataset.guest) next.guest = chip.dataset.guest;
    if(chip.dataset.zone) next.zone = chip.dataset.zone;

    applyFilters(next);
  }});

  document.addEventListener("DOMContentLoaded", ()=>{{
    populateZones();
    applyFilters({{guest:"all", zone:"all"}});
    const reset=document.getElementById("mfReset");
    if(reset) reset.addEventListener("click", ()=>applyFilters({{guest:"all", zone:"all"}}));
  }});
}})();
"""
    return js.rstrip() + "\n\n" + block + "\n"

def main():
    if not INDEX.exists():
        print("❌ Non trovo index.html. Esegui lo script dalla cartella del sito.")
        return

    # index
    backup(INDEX)
    html = read(INDEX)
    html = ensure_rel_img_paths(html)
    html = add_lazy_imgs(html)
    html = remove_hero_smartbar(html)
    html = remove_heavy_filters(html)
    html = inject_mini_filters(html)
    html = make_cards_clickable_and_clean(html)
    write(INDEX, html)

    # css
    if CSS.exists():
        backup(CSS)
        css = read(CSS)
        css = inject_css(css)
        write(CSS, css)

    # js
    if JS.exists():
        backup(JS)
        js = read(JS)
        js = inject_js(js)
        write(JS, js)

    print("✅ LITE CLEAN PACK (A) applicato.")
    print("➡️ Test: python3 -m http.server 8000  →  http://localhost:8000")
    print("➡️ Pubblica: git add -A && git commit -m \"Clean UX\" && git push")

if __name__ == "__main__":
    main()
