// Подбор букв (DESIGN.md, «Слайдер»): сначала случайные символы того же регистра
// (кириллица + цифры), затем буквы встают на место слева направо.
// Экранные чтецы получают полный текст сразу: он остаётся в DOM, а анимация — в слое aria-hidden.

import { prefersReducedMotion } from "./motion.js";

const FRAME_MS = 28;
const START_MS = 200;
const TOTAL_MS = 600;

const UPPER = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ";
const LOWER = UPPER.toLowerCase();
const DIGITS = "0123456789";

const timers = new WeakMap();

function pick(chars) {
  return chars[Math.floor(Math.random() * chars.length)];
}

function randomLike(char) {
  if (/\d/.test(char)) return pick(DIGITS);
  if (char !== char.toLowerCase()) return pick(UPPER);
  if (char !== char.toUpperCase()) return pick(LOWER);
  return char; // пробелы, дефисы, скобки остаются на месте
}

// Оборачивает текст: настоящий текст держит место и читается, поверх — слой анимации
function prepare(el) {
  if (el.dataset.scrambleReady) return;
  const text = el.textContent.trim();
  const real = document.createElement("span");
  real.className = "scramble__real";
  real.textContent = text;
  const fx = document.createElement("span");
  fx.className = "scramble__fx";
  fx.setAttribute("aria-hidden", "true");
  el.replaceChildren(real, fx);
  el.classList.add("scramble");
  el.dataset.scrambleReady = "1";
}

export function scramble(el) {
  prepare(el);
  clearInterval(timers.get(el));
  el.classList.remove("is-scrambling");
  if (prefersReducedMotion()) return;

  const text = el.querySelector(".scramble__real").textContent;
  const fx = el.querySelector(".scramble__fx");
  const startedAt = performance.now();

  const frame = () => {
    const elapsed = performance.now() - startedAt;
    if (elapsed >= TOTAL_MS) {
      clearInterval(timers.get(el));
      el.classList.remove("is-scrambling");
      return;
    }
    const progress = Math.max(0, (elapsed - START_MS) / (TOTAL_MS - START_MS));
    const settled = Math.floor(progress * text.length);
    fx.textContent = [...text].map((ch, i) => (i < settled ? ch : randomLike(ch))).join("");
  };

  el.classList.add("is-scrambling");
  frame();
  timers.set(el, setInterval(frame, FRAME_MS));
}
