document.addEventListener("DOMContentLoaded", () => {
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
