// Форма заявки: маска телефона +7, проверка полей, отправка через fetch с CSRF,
// ошибки по полям из JSON, модалки загрузки / успеха / ошибки.

import { createModal } from "./modal.js";
import { prefersReducedMotion } from "./motion.js";

const PHONE_DIGITS = 10;

// «+7 (999) 123-45-67», «89991234567», «9991234567» → 10 цифр без кода страны
function phoneDigits(value) {
  let digits = value.replace(/\D/g, "");
  if (value.trim().startsWith("+7")) digits = digits.slice(1);
  // Вставили «8999…» или «7999…» целиком (в том числе после префикса «+7 (»)
  if (digits.length > PHONE_DIGITS && (digits[0] === "7" || digits[0] === "8")) {
    digits = digits.slice(1);
  }
  return digits.slice(0, PHONE_DIGITS);
}

// 10 цифр → «+7 (999) 123-45-67», по мере ввода
function formatPhone(digits) {
  if (!digits) return "";
  let out = "+7 (" + digits.slice(0, 3);
  if (digits.length >= 3) out += ")";
  if (digits.length > 3) out += " " + digits.slice(3, 6);
  if (digits.length > 6) out += "-" + digits.slice(6, 8);
  if (digits.length > 8) out += "-" + digits.slice(8, 10);
  return out;
}

function initPhoneMask(input) {
  input.addEventListener("focus", () => {
    if (!input.value) input.value = "+7 (";
  });
  input.addEventListener("blur", () => {
    if (!phoneDigits(input.value)) input.value = "";
  });
  input.addEventListener("input", (event) => {
    let digits = phoneDigits(input.value);
    // Стёрли скобку, пробел или дефис — стираем и цифру перед ними
    if (event.inputType === "deleteContentBackward" && digits === input.dataset.digits) {
      digits = digits.slice(0, -1);
    }
    input.dataset.digits = digits;
    input.value = digits ? formatPhone(digits) : "+7 (";
  });
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : "";
}

export function initLeadForm(form) {
  const submit = form.querySelector('[type="submit"]');
  const nameInput = form.elements.name;
  const phoneInput = form.elements.phone;
  const sourceInput = form.elements.source;
  const carModelInput = form.elements.car_model;
  const modal = createModal(document.querySelector("[data-lead-modal]"), {
    onRetry: () => send(),
  });
  let sending = false;

  initPhoneMask(phoneInput);

  const setError = (field, message) => {
    const input = form.elements[field];
    const box = form.querySelector(`#id_${field}-error`);
    if (!input || !box) return;
    input.setAttribute("aria-invalid", message ? "true" : "false");
    box.querySelector(".field__error-text").textContent = message || "";
    box.hidden = !message;
  };

  const clearErrors = () => {
    ["name", "phone", "car_model"].forEach((field) => setError(field, ""));
  };

  const validate = () => {
    const errors = {};
    if (!nameInput.value.trim()) errors.name = "Укажите имя";
    const digits = phoneDigits(phoneInput.value);
    if (!digits) errors.phone = "Укажите телефон";
    else if (digits.length !== PHONE_DIGITS) errors.phone = "Введите номер в формате +7 (999) 123-45-67";
    return errors;
  };

  const showErrors = (errors) => {
    Object.entries(errors).forEach(([field, message]) =>
      setError(field, Array.isArray(message) ? message[0] : message),
    );
    const first = Object.keys(errors)[0];
    form.elements[first]?.focus();
  };

  const setSending = (value) => {
    sending = value;
    submit.disabled = value;
    submit.setAttribute("aria-busy", String(value));
  };

  async function send() {
    if (sending) return;
    clearErrors();
    const errors = validate();
    if (Object.keys(errors).length) {
      modal.close();
      showErrors(errors);
      return;
    }

    setSending(true);
    modal.show("loading", { focusAfterClose: submit });
    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-CSRFToken": getCookie("csrftoken"), "X-Requested-With": "fetch" },
        credentials: "same-origin",
      });
      const data = await response.json().catch(() => ({}));

      if (response.ok && data.ok) {
        form.reset();
        phoneInput.dataset.digits = "";
        sourceInput.value = "contacts";
        modal.show("success");
      } else if (response.status === 400 && data.errors) {
        modal.close();
        showErrors(data.errors);
      } else {
        modal.show("error"); // введённые данные остаются в форме
      }
    } catch {
      modal.show("error");
    } finally {
      setSending(false);
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    send();
  });

  // Кнопки, ведущие к форме: подставляют модель авто и источник заявки
  document.addEventListener("click", (event) => {
    const link = event.target.closest("[data-lead-source]");
    if (!link || link.closest('[aria-hidden="true"]')) return;
    event.preventDefault();
    sourceInput.value = link.dataset.leadSource;
    if (link.dataset.carModel) carModelInput.value = link.dataset.carModel;
    form.closest("section").scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth" });
    nameInput.focus({ preventScroll: true });
  });
}
