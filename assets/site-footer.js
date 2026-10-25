/*! Shared site footer: copyright year, mobile nav menu, and nav dropdowns. */
(function initSiteFooter() {
  const yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }
})();

(function initNavMenu() {
  const header = document.querySelector(".site-header");
  const navRow = header && header.querySelector(".nav");
  const nav = header && header.querySelector(".nav-links");
  const utils = header && header.querySelector(".header-utils");
  if (!header || !navRow || !nav || !utils) return;

  if (!nav.id) nav.id = "primaryNav";

  let toggle = header.querySelector(".nav-menu-toggle");
  if (!toggle) {
    toggle = document.createElement("button");
    toggle.className = "nav-menu-toggle";
    toggle.type = "button";
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", nav.id);
    toggle.setAttribute("aria-label", "Open menu");
    toggle.innerHTML = '<span class="nav-menu-toggle-bars" aria-hidden="true"></span>';
    utils.prepend(toggle);
  } else {
    toggle.setAttribute("aria-controls", nav.id);
  }

  function setOpen(open) {
    header.classList.toggle("is-nav-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    if (!open) {
      nav.querySelectorAll("[data-nav-drop].is-open").forEach((drop) => {
        drop.classList.remove("is-open");
        const dropToggle = drop.querySelector(".nav-drop-toggle");
        if (dropToggle) dropToggle.setAttribute("aria-expanded", "false");
      });
    }
  }

  toggle.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    setOpen(!header.classList.contains("is-nav-open"));
  });

  nav.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link) return;
    setOpen(false);
  });

  document.addEventListener("click", (event) => {
    if (!header.classList.contains("is-nav-open")) return;
    if (event.target.closest(".nav-links") || event.target.closest(".nav-menu-toggle")) return;
    setOpen(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
  });

  window.addEventListener("resize", () => {
    if (window.getComputedStyle(toggle).display === "none") setOpen(false);
  });
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
