/*! Shared site footer: copyright year + Guides dropdown. */
(function initSiteFooter() {
  const yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }
})();

(function initNavDrops() {
  const drops = Array.from(document.querySelectorAll("[data-nav-drop]"));
  if (!drops.length) return;

  function closeDrop(drop) {
    drop.classList.remove("is-open");
    const toggle = drop.querySelector(".nav-drop-toggle");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }

  function closeAll(except) {
    drops.forEach((drop) => {
      if (drop !== except) closeDrop(drop);
    });
  }

  drops.forEach((drop) => {
    const toggle = drop.querySelector(".nav-drop-toggle");
    if (!toggle) return;
    toggle.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const willOpen = !drop.classList.contains("is-open");
      closeAll(drop);
      drop.classList.toggle("is-open", willOpen);
      toggle.setAttribute("aria-expanded", willOpen ? "true" : "false");
    });
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-nav-drop]")) return;
    closeAll();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAll();
  });
})();
