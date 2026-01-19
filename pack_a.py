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
        bp = p.with_suffix(p.suffix + f".bak-{STAMP}")
        bp.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

def ensure_lazy_images(html: str) -> str:
    def repl(m):
        tag = m.group(0)
        if "loading=" in tag:
            return tag
        return tag.replace("<img", '<img loading="lazy" decoding="async"', 1)
    return re.sub(r"<img\b[^>]*>", repl, html, flags=re.IGNORECASE)

def fix_absolute_img_paths(html: str) -> str:
    html = re.sub(r'src="/img/', 'src="img/', html, flags=re.IGNORECASE)
    html = re.sub(r'href="/img/', 'href="img/', html, flags=re.IGNORECASE)
    return html

def inject_wa_fab(html: str) -> str:
    if 'id="waSticky"' in html:
        return html
    fab = """
  <!-- WhatsApp Sticky FAB (Pack A) -->
  <a id="waSticky" class="wa-fab" href="#" target="_blank" rel="noopener" aria-label="Contattaci su WhatsApp">
    <span class="wa-fab__icon" aria-hidden="true">💬</span>
    <span class="wa-fab__text">WhatsApp</span>
  </a>
"""
    return re.sub(r"</body>", fab + "\n</body>", html, flags=re.IGNORECASE, count=1)

def make_cards_image_clickable(html: str) -> str:
    def fix_card(card: str) -> str:
        if re.search(r"<a[^>]*>\s*<img", card, flags=re.IGNORECASE):
            return card
        m = re.search(r'<a[^>]*href="([^"]*case/[^"]+)"', card, flags=re.IGNORECASE)
        if not m:
            return card
        href = m.group(1)
        return re.sub(r'(<img\b[^>]*>)', rf'<a class="card__mediaLink" href="{href}">\1</a>', card, flags=re.IGNORECASE, count=1)
    return re.sub(
        r"(<article\b[^>]*class=\"card\"[\s\S]*?</article>)",
        lambda m: fix_card(m.group(1)),
        html,
        flags=re.IGNORECASE
    )

def add_action_bar_to_case(html: str) -> str:
    if "action-bar" in html:
        return html
    mpdf = re.search(r'href="([^"]+\.pdf)"', html, flags=re.IGNORECASE)
    if not mpdf:
        return html
    pdf_href = mpdf.group(1)

    mt = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.IGNORECASE | re.DOTALL)
    title = re.sub(r"<[^>]+>", "", mt.group(1)).strip() if mt else "questa casa"

    bar = f"""
      <!-- Pack A: Action Bar -->
      <div class="action-bar">
        <a class="btn btn--primary pdf-btn" href="{pdf_href}" target="_blank" rel="noopener">Apri scheda (PDF)</a>
        <a class="btn btn--secondary wa-btn" id="waProperty" href="#" target="_blank" rel="noopener"
           data-property-name="{title}">Chiedi disponibilità su WhatsApp</a>
      </div>
"""
    return re.sub(r"(</h1>)", r"\1" + bar, html, flags=re.IGNORECASE, count=1)

def ensure_pack_a_css(css: str) -> str:
    if "/* === PACK A UI === */" in css:
        return css
    block = r"""
/* === PACK A UI === */
:root{ --wa:#25D366; }

/* Sticky WhatsApp button */
.wa-fab{
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 9999;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 999px;
  background: rgba(37, 211, 102, .14);
  border: 1px solid rgba(37, 211, 102, .35);
  backdrop-filter: blur(10px);
  box-shadow: 0 24px 70px rgba(0,0,0,.45);
  transition: transform .18s ease, background .18s ease;
}
.wa-fab:hover{ transform: translateY(-2px); background: rgba(37, 211, 102, .18); }
.wa-fab__icon{
  width: 34px; height: 34px;
  display: grid; place-items: center;
  border-radius: 999px;
  background: rgba(37, 211, 102, .22);
  border: 1px solid rgba(37, 211, 102, .35);
}
.wa-fab__text{ font-weight: 800; letter-spacing: .2px; }

/* mobile: wide & comfy */
@media (max-width: 520px){
  .wa-fab{
    left: 12px; right: 12px;
    bottom: 12px;
    justify-content: center;
  }
}

/* Action bar in property pages */
.action-bar{
  margin: 14px 0 18px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
@media (max-width: 520px){
  .action-bar .btn{ width: 100%; }
}

/* Meta chips */
.meta li{
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.10);
}

/* Card media link */
.card__mediaLink{ display:block; }

/* Lightbox overlay */
.lb{
  position: fixed; inset: 0; z-index: 10000;
  display: none; align-items: center; justify-content: center;
  background: rgba(0,0,0,.72); backdrop-filter: blur(8px);
}
.lb.open{ display:flex; }
.lb__inner{
  width: min(1100px, 94vw);
  height: min(78vh, 680px);
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.18);
  box-shadow: 0 28px 90px rgba(0,0,0,.55);
  position: relative;
  background: rgba(10,12,18,.55);
}
.lb__img{ width:100%; height:100%; object-fit: contain; }
.lb__x{
  position:absolute; top:12px; right:12px;
  width:44px; height:44px;
  display:grid; place-items:center;
  border-radius:14px;
  background: rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.14);
}
.lb__nav{
  position:absolute; top:50%;
  transform: translateY(-50%);
  width:44px; height:60px;
  display:grid; place-items:center;
  border-radius:16px;
  background: rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.14);
}
.lb__prev{ left:12px; } .lb__next{ right:12px; }

@media (prefers-reduced-motion: reduce){
  *{ transition:none !important; animation:none !important; }
}
"""
    return css + "\n" + block

def ensure_pack_a_js(js: str) -> str:
    if "// === PACK A: Sticky WhatsApp + Lightbox ===" in js:
        return js
    block = r"""
// === PACK A: Sticky WhatsApp + Lightbox ===
(function(){
  const DEFAULT_WA_NUMBER = "393292272939";
  function buildWA(msg){
    try{
      if(typeof buildWhatsAppLink === "function") return buildWhatsAppLink(msg);
    }catch(e){}
    const base = "https://wa.me/";
    const num = (typeof WHATSAPP_NUMBER !== "undefined" ? WHATSAPP_NUMBER : DEFAULT_WA_NUMBER);
    return `${base}${num}?text=${encodeURIComponent(msg)}`;
  }

  function setStickyWA(){
    const a = document.getElementById("waSticky");
    if(!a) return;

    const propertyBtn = document.getElementById("waProperty");
    const propertyName = propertyBtn?.dataset?.propertyName;

    const msg = propertyName
      ? `Ciao! Vorrei disponibilità per: ${propertyName}.`
      : "Ciao! Vorrei ricevere disponibilità per una casa/villa a Gallipoli (estate).";

    a.href = buildWA(msg);

    if(propertyBtn){
      propertyBtn.href = buildWA(msg);
    }
  }

  function initLightbox(){
    const isCase = window.location.pathname.includes("/case/");
    if(!isCase) return;

    const imgs = Array.from(document.querySelectorAll("img"))
      .filter(img => {
        const src = (img.getAttribute("src")||"").toLowerCase();
        return src.match(/\.(jpg|jpeg|png|webp)$/);
      });

    if(!imgs.length) return;

    let lb = document.querySelector(".lb");
    if(!lb){
      lb = document.createElement("div");
      lb.className = "lb";
      lb.innerHTML = `
        <div class="lb__inner" role="dialog" aria-modal="true">
          <img class="lb__img" alt="">
          <button class="lb__x" aria-label="Chiudi">✕</button>
          <button class="lb__nav lb__prev" aria-label="Foto precedente">‹</button>
          <button class="lb__nav lb__next" aria-label="Foto successiva">›</button>
        </div>
      `;
      document.body.appendChild(lb);
    }

    const imgEl = lb.querySelector(".lb__img");
    const btnX = lb.querySelector(".lb__x");
    const btnPrev = lb.querySelector(".lb__prev");
    const btnNext = lb.querySelector(".lb__next");

    let i = 0;
    function openAt(idx){
      i = (idx + imgs.length) % imgs.length;
      imgEl.src = imgs[i].getAttribute("src");
      imgEl.alt = imgs[i].alt || "Foto";
      lb.classList.add("open");
      document.body.style.overflow = "hidden";
    }
    function close(){
      lb.classList.remove("open");
      document.body.style.overflow = "";
      imgEl.removeAttribute("src");
    }
    function prev(){ openAt(i-1); }
    function next(){ openAt(i+1); }

    imgs.forEach((im, idx)=>{
      im.style.cursor = "zoom-in";
      im.addEventListener("click", ()=>openAt(idx));
    });

    btnX.addEventListener("click", close);
    btnPrev.addEventListener("click", prev);
    btnNext.addEventListener("click", next);
    lb.addEventListener("click", (e)=>{ if(e.target === lb) close(); });

    window.addEventListener("keydown", (e)=>{
      if(!lb.classList.contains("open")) return;
      if(e.key === "Escape") close();
      if(e.key === "ArrowLeft") prev();
      if(e.key === "ArrowRight") next();
    });

    let startX = null;
    lb.addEventListener("touchstart", (e)=>{ startX = e.touches?.[0]?.clientX ?? null; }, {passive:true});
    lb.addEventListener("touchend", (e)=>{
      if(startX === null) return;
      const endX = e.changedTouches?.[0]?.clientX ?? startX;
      const dx = endX - startX;
      if(Math.abs(dx) > 40){
        dx > 0 ? prev() : next();
      }
      startX = null;
    }, {passive:true});
  }

  document.addEventListener("DOMContentLoaded", ()=>{
    setStickyWA();
    initLightbox();
  });
})();
"""
    return js + "\n" + block

def main():
    for p in [INDEX, CSS, JS]:
        backup(p)

    html = INDEX.read_text(encoding="utf-8")
    html = fix_absolute_img_paths(html)
    html = ensure_lazy_images(html)
    html = make_cards_image_clickable(html)
    html = inject_wa_fab(html)
    INDEX.write_text(html, encoding="utf-8")

    if CASE_DIR.exists():
        for f in CASE_DIR.glob("*.html"):
            backup(f)
            h = f.read_text(encoding="utf-8")
            h = fix_absolute_img_paths(h)
            h = ensure_lazy_images(h)
            h = add_action_bar_to_case(h)
            h = inject_wa_fab(h)
            f.write_text(h, encoding="utf-8")

    css = CSS.read_text(encoding="utf-8")
    CSS.write_text(ensure_pack_a_css(css), encoding="utf-8")

    js = JS.read_text(encoding="utf-8")
    JS.write_text(ensure_pack_a_js(js), encoding="utf-8")

    print("✅ PACK A applicato: sticky WhatsApp (anche schede) + lightbox + action bar PDF/WA + lazyload + UI polish.")
    print("➡️ Test: python3 -m http.server 8000  →  http://localhost:8000")

if __name__ == "__main__":
    main()
