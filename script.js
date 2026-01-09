// CONFIGURA QUI IL TUO NUMERO WHATSAPP (formato internazionale, senza + e senza spazi)
const WHATSAPP_NUMBER = "393292272939"; 

function buildWhatsAppLink(message) {
  const base = "https://wa.me/";
  const text = encodeURIComponent(message);
  return `${base}${WHATSAPP_NUMBER}?text=${text}`;
}

function formatDate(d) {
  if (!d) return "";
  // d in formato yyyy-mm-dd
  return d;
}

function init() {
  document.getElementById("year").textContent = new Date().getFullYear();

  const defaultMsg = "Ciao! Vorrei ricevere disponibilità per una casa/villa in Salento.";
  const waHero = document.getElementById("waHero");
  const waFooter = document.getElementById("waFooter");

  waHero.href = buildWhatsAppLink(defaultMsg);
  waFooter.href = buildWhatsAppLink(defaultMsg);

  const form = document.getElementById("requestForm");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(form);
    const checkin = formatDate(data.get("checkin"));
    const checkout = formatDate(data.get("checkout"));
    const guests = data.get("guests");
    const budget = data.get("budget") || "";
    const notes = data.get("notes") || "";

    const msg =
`Ciao! Vorrei una proposta per il Salento.
- Arrivo: ${checkin}
- Partenza: ${checkout}
- Ospiti: ${guests}
- Budget: ${budget}
- Note: ${notes}`.trim();

    window.location.href = buildWhatsAppLink(msg);
  });
}

document.addEventListener("DOMContentLoaded", init);
