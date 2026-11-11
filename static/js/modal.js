// Модалка отправки заявки: состояния loading / success / error в одной карточке.
// Удерживает фокус внутри, закрывается по Esc (кроме загрузки), возвращает фокус на кнопку формы.

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function createModal(dialog, { onRetry } = {}) {
  let state = null;
  let returnFocus = null;

  const visibleFocusables = () =>
    [...dialog.querySelectorAll(FOCUSABLE)].filter((el) => el.offsetParent !== null);

  const show = (next, { focusAfterClose } = {}) => {
    if (focusAfterClose) returnFocus = focusAfterClose;
    state = next;
    dialog.dataset.state = next;
    dialog.querySelectorAll(".modal__state").forEach((panel) => {
      panel.hidden = panel.dataset.state !== next;
    });
    dialog.setAttribute("aria-labelledby", `lead-modal-title-${next}`);
    dialog.querySelector("[data-modal-close]").hidden = next === "loading";

    if (!dialog.open) dialog.showModal();

    const target = dialog.querySelector(`[data-state="${next}"] [data-autofocus]`);
    if (target) target.focus();
    else {
      dialog.tabIndex = -1;
      dialog.focus();
    }
  };

  const close = () => {
    if (dialog.open) dialog.close();
  };

  dialog.addEventListener("close", () => {
    state = null;
    returnFocus?.focus();
  });

  // Esc: во время отправки закрыть нельзя
  dialog.addEventListener("cancel", (event) => {
    if (state === "loading") event.preventDefault();
  });

  dialog.addEventListener("click", (event) => {
    if (event.target.closest("[data-modal-close]")) close();
    if (event.target.closest("[data-modal-retry]")) onRetry?.();
  });

  // Удержание фокуса: Tab по кругу внутри карточки
  dialog.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    const items = visibleFocusables();
    if (!items.length) {
      event.preventDefault();
      return;
    }
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  return { show, close };
}
