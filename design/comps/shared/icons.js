// One stroke icon set (Lucide-style geometry, 24 grid, 2px stroke) shared by every direction.
(() => {
  const s = (id, body) => `<symbol id="i-${id}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${body}</symbol>`;
  const sprite = [
    s("urgent", '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>'),
    s("routine", '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    s("arrow", '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>'),
    s("arrow-up", '<path d="M12 19V5"/><path d="m6 11 6-6 6 6"/>'),
    s("review", '<path d="M12 2 22 12 12 22 2 12Z"/><path d="M12 8v5"/><path d="M12 16h.01"/>'),
    s("auto", '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/><path d="M5 6v12"/>'),
    s("check", '<path d="M20 6 9 17l-5-5"/>'),
    s("override", '<path d="M17 3a2.8 2.8 0 0 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>'),
    s("escalate", '<path d="m17 11-5-5-5 5"/><path d="m17 18-5-5-5 5"/>'),
    s("search", '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>'),
    s("queue", '<path d="M3 6h18"/><path d="M3 12h18"/><path d="M3 18h12"/>'),
    s("results", '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>'),
    s("label", '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>'),
    s("about", '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4"/><path d="M12 8h.01"/>'),
    s("back", '<path d="m15 18-6-6 6-6"/>'),
    s("chev", '<path d="m6 9 6 6 6-6"/>'),
    s("clock", '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    s("doc", '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/>'),
    s("x", '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'),
    s("filter", '<path d="M3 5h18l-7 8v6l-4 2v-8Z"/>'),
  ].join("");
  document.body.insertAdjacentHTML("afterbegin", `<svg width="0" height="0" style="position:absolute" aria-hidden="true">${sprite}</svg>`);
})();
window.ic = (id, cls = "ic") => `<svg class="${cls}" aria-hidden="true"><use href="#i-${id}"/></svg>`;
