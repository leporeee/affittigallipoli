// CONFIGURA QUI IL TUO NUMERO WHATSAPP (formato internazionale, senza + e senza spazi)
const WHATSAPP_NUMBER = "393292272939";

function buildWhatsAppLink(message) {
  const base = "https://wa.me/";
  const text = encodeURIComponent(message);
  return `${base}${WHATSAPP_NUMBER}?text=${text}`;
}

function safeText(s) {
  return (s || "").toString().trim();
}

function formatDate(d) {
  // d in formato yyyy-mm-dd
  return safeText(d);
}

function prefersReducedMotion() {
  return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function initHeroSlider() {
  const heroSlides = Array.from(document.querySelectorAll(".hero-slide"));
  if (heroSlides.length <= 1 || prefersReducedMotion()) return;

  let i = 0;
  const show = (idx) => {
    heroSlides.forEach((s, k) => s.classList.toggle("is-active", k === idx));
  };

  show(0);
  window.setInterval(() => {
    i = (i + 1) % heroSlides.length;
    show(i);
  }, 5200);
}

function initWhatsAppLinks() {
  const defaultMsg = "Ciao! Vorrei ricevere disponibilità per una casa/villa a Gallipoli.";

  const waHero = document.getElementById("waHero");
  const waFooter = document.getElementById("waFooter");
  const waFab = document.getElementById("waFab");

  const href = buildWhatsAppLink(defaultMsg);
  if (waHero) waHero.href = href;
  if (waFooter) waFooter.href = href;
  if (waFab) waFab.href = href;

  // Bottoni "Chiedi su WhatsApp" sulle card
  document.querySelectorAll(".js-wa-card").forEach((a) => {
    const house = safeText(a.getAttribute("data-house"));
    const zone = safeText(a.getAttribute("data-zone"));
    const guests = safeText(a.getAttribute("data-guests"));

    const msg = [
      `Ciao! Vorrei disponibilità per ${house}.`,
      zone ? `Zona: ${zone}` : "",
      guests ? `Ospiti: ${guests}` : "",
      "Grazie!"
    ].filter(Boolean).join("\n");

    a.setAttribute("href", buildWhatsAppLink(msg));
    a.setAttribute("target", "_blank");
    a.setAttribute("rel", "noopener");
  });
}

function initYear() {
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
}

function initRequestForm() {
  const form = document.getElementById("requestForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(form);

    const checkin = formatDate(data.get("checkin"));
    const checkout = formatDate(data.get("checkout"));
    const guests = safeText(data.get("guests"));
    const budget = safeText(data.get("budget"));
    const notes = safeText(data.get("notes"));

    const msg = [
      "Ciao! Vorrei una proposta per Gallipoli / Salento.",
      checkin ? `- Arrivo: ${checkin}` : "",
      checkout ? `- Partenza: ${checkout}` : "",
      guests ? `- Ospiti: ${guests}` : "",
      budget ? `- Budget: ${budget}` : "",
      notes ? `- Note: ${notes}` : ""
    ].filter(Boolean).join("\n");

    window.location.href = buildWhatsAppLink(msg);
  });
}

function parseIntSafe(v) {
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? n : null;
}

function initCardsClickthrough() {
  // Click su tutta la card -> apre la scheda
  document.querySelectorAll(".property-card").forEach((card) => {
    const href = card.getAttribute("data-href");
    if (!href) return;

    card.addEventListener("click", (e) => {
      // Non hijackare click su link/bottoni/inputs
      if (e.target && e.target.closest("a, button, input, textarea, select, label")) return;
      window.location.href = href;
    });

    // Cursor e accessibilità
    card.setAttribute("role", "link");
    card.setAttribute("tabindex", "0");
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        window.location.href = href;
      }
    });
  });
}

function initRevealAnimations() {
  if (prefersReducedMotion() || !('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add("in");
      });
    },
    { threshold: 0.12 }
  );

  document.querySelectorAll(
    ".hero__grid, .section__head, .step, .option-card, .filterbar, .property-card, .form"
  ).forEach((el) => {
    el.classList.add("reveal");
    observer.observe(el);
  });
}

function initFiltersAndSearch() {
  const optionCards = Array.from(document.querySelectorAll(".option-card"));
  const cards = Array.from(document.querySelectorAll(".property-card"));
  const resultsMeta = document.getElementById("resultsMeta");
  const btnShowAll = document.getElementById("btnShowAll");
  const searchInput = document.getElementById("searchInput");
  const sortSelect = document.getElementById("sortSelect");
  const cardsGrid = document.getElementById("cardsGrid");

  if (!cards.length || !cardsGrid) return;

  let activeRange = null; // {min, max}
  let searchTerm = "";

  const getGuests = (card) => {
    const attr = card.getAttribute("data-guests");
    const n = parseIntSafe(attr);
    if (n != null) return n;

    // fallback: prova a leggere "👥 6 ospiti" dal testo
    const m = card.textContent.match(/\b(\d+)\s*ospiti\b/i);
    return m ? parseIntSafe(m[1]) : null;
  };

  const getZone = (card) => safeText(card.getAttribute("data-zone"));
  const getName = (card) => safeText(card.getAttribute("data-name"));

  const cardMatches = (card) => {
    // range
    if (activeRange) {
      const g = getGuests(card);
      if (g == null) return false;
      if (g < activeRange.min || g > activeRange.max) return false;
    }

    // search
    if (searchTerm) {
      const hay = `${getName(card)} ${getZone(card)} ${safeText(card.textContent)}`.toLowerCase();
      if (!hay.includes(searchTerm)) return false;
    }

    return true;
  };

  const updateMeta = (shown, total) => {
    if (!resultsMeta) return;

    const rangeTxt = activeRange
      ? (activeRange.max >= 99
          ? `Fascia: ${activeRange.min}+ posti`
          : `Fascia: ${activeRange.min}–${activeRange.max} posti`)
      : "Tutte le fasce";
    const searchTxt = searchTerm ? ` • Ricerca: \"${searchTerm}\"` : "";

    resultsMeta.textContent = `Mostrando ${shown} su ${total}. ${rangeTxt}${searchTxt}`;
  };

  const setCardVisible = (card, visible) => {
    // animazione (leggera)
    if (visible) {
      card.classList.remove("is-gone");
      requestAnimationFrame(() => card.classList.remove("is-hidden"));
    } else {
      card.classList.add("is-hidden");
      window.setTimeout(() => card.classList.add("is-gone"), 220);
    }
  };

  const apply = () => {
    let shown = 0;
    const total = cards.length;

    cards.forEach((card) => {
      const ok = cardMatches(card);
      setCardVisible(card, ok);
      if (ok) shown += 1;
    });

    updateMeta(shown, total);
    if (btnShowAll) btnShowAll.hidden = !(activeRange || searchTerm);
  };

  const setActiveOption = (btn) => {
    optionCards.forEach((b) => {
      const isActive = b === btn;
      b.classList.toggle("is-active", isActive);
      b.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  };

  // Click sulle fasce
  optionCards.forEach((btn) => {
    btn.addEventListener("click", () => {
      const min = parseIntSafe(btn.getAttribute("data-min"));
      const max = parseIntSafe(btn.getAttribute("data-max"));
      if (min == null || max == null) return;

      // toggle: clicchi la stessa -> reset
      if (activeRange && activeRange.min === min && activeRange.max === max) {
        activeRange = null;
        setActiveOption(null);
      } else {
        activeRange = { min, max };
        setActiveOption(btn);
      }

      apply();
      // scroll morbido alla griglia
      const target = document.getElementById("case");
      if (target) target.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "start" });
    });
  });

  // Mostra tutte
  if (btnShowAll) {
    btnShowAll.addEventListener("click", () => {
      activeRange = null;
      searchTerm = "";
      if (searchInput) searchInput.value = "";
      setActiveOption(null);
      apply();
    });
  }

  // Search
  if (searchInput) {
    let t = null;
    searchInput.addEventListener("input", () => {
      window.clearTimeout(t);
      t = window.setTimeout(() => {
        searchTerm = safeText(searchInput.value).toLowerCase();
        apply();
      }, 80);
    });
  }

  // Sorting
  const sortCards = (mode) => {
    const list = Array.from(cardsGrid.querySelectorAll(".property-card"));

    const by = {
      "featured": () => 0,
      "guests-asc": (a, b) => (getGuests(a) ?? 999) - (getGuests(b) ?? 999),
      "guests-desc": (a, b) => (getGuests(b) ?? -1) - (getGuests(a) ?? -1),
      "zone-asc": (a, b) => getZone(a).localeCompare(getZone(b), "it", { sensitivity: "base" }),
      "name-asc": (a, b) => getName(a).localeCompare(getName(b), "it", { sensitivity: "base" })
    };

    if (!by[mode] || mode === "featured") {
      // non riordina: mantiene l'ordine in HTML
      return;
    }

    list.sort(by[mode]);
    const frag = document.createDocumentFragment();
    list.forEach((el) => frag.appendChild(el));
    cardsGrid.appendChild(frag);
  };

  if (sortSelect) {
    sortSelect.addEventListener("change", () => {
      sortCards(sortSelect.value);
      // dopo riordino, riapplica per mantenere le classi corrette
      apply();
    });
  }

  // primo pass
  apply();
}

function init() {
  initYear();
  initHeroSlider();
  initWhatsAppLinks();
  initRequestForm();
  initCardsClickthrough();
  initRevealAnimations();
  initFiltersAndSearch();
}

document.addEventListener("DOMContentLoaded", init);

// export (utile se vuoi riusare la funzione nei file delle case)
window.buildWhatsAppLink = buildWhatsAppLink;


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
// WhatsApp floating: show on desktop after scroll, hide near footer
(function(){
  const fab = document.getElementById("waSticky");
  if(!fab) return;

  const DESKTOP_SCROLL_SHOW = 160;

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

  const footer = document.querySelector("footer");
  if(footer && "IntersectionObserver" in window){
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(e=>{
        if(window.innerWidth > 520){
          const shouldShow = !e.isIntersecting && window.scrollY > DESKTOP_SCROLL_SHOW;
          fab.classList.toggle("is-visible", shouldShow);
        }
      });
    }, { threshold: 0.15 });
    io.observe(footer);
  }
})();
