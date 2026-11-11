// Бургер-меню (< 768px): открывается кнопкой, закрывается по Esc, по выбору пункта и при расширении экрана

const desktop = window.matchMedia("(min-width: 768px)");

export function initMenu(header) {
  const button = header.querySelector("[data-burger]");
  const nav = header.querySelector(".header__nav");

  const setOpen = (open, { returnFocus = false } = {}) => {
    header.classList.toggle("is-open", open);
    button.setAttribute("aria-expanded", String(open));
    if (!open && returnFocus) button.focus();
  };

  button.addEventListener("click", () => setOpen(!header.classList.contains("is-open")));

  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) setOpen(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && header.classList.contains("is-open")) {
      setOpen(false, { returnFocus: true });
    }
  });

  desktop.addEventListener("change", (event) => {
    if (event.matches) setOpen(false);
  });
}
