// Слайдер «Готовые комплекты» (DESIGN.md): стрелки, клик по соседней карточке, свайп,
// клавиши-стрелки, цикличная прокрутка, счётчик. Без автопрокрутки, паузы и точек.

import { scramble } from "./scramble.js";

const SWIPE_THRESHOLD = 50;
const FOCUSABLE = "a[href], button, input, select, textarea, [tabindex]";

export function initSlider(root) {
  const slides = [...root.querySelectorAll(".kit")];
  const count = slides.length;
  if (count < 2) return;

  const controls = root.querySelector(".slider__controls");
  const current = root.querySelector(".slider__current");
  const positions = new Array(count).fill(null);
  let active = 0;

  // Положение карточки относительно активной: …, -1, 0, 1, … по кратчайшему пути по кругу
  const relative = (index) => {
    let pos = index - active;
    if (pos > count / 2) pos -= count;
    if (pos < -count / 2) pos += count;
    return pos;
  };

  const render = () => {
    slides.forEach((slide, index) => {
      const pos = relative(index);
      const prev = positions[index];
      // Карточка, перескочившая с одного края на другой, не должна пролетать через экран
      slide.classList.toggle("no-transition", prev === null || Math.abs(pos - prev) > 1);
      slide.style.setProperty("--pos", pos);
      slide.classList.toggle("is-active", pos === 0);
      slide.classList.toggle("is-side", Math.abs(pos) === 1);
      slide.setAttribute("aria-hidden", String(pos !== 0));
      slide.querySelectorAll(FOCUSABLE).forEach((el) => {
        if (pos === 0) el.removeAttribute("tabindex");
        else el.setAttribute("tabindex", "-1");
      });
      positions[index] = pos;
    });
    current.textContent = String(active + 1).padStart(2, "0");
  };

  const enter = (slide) => {
    slide.classList.remove("is-entering");
    void slide.offsetWidth; // перезапуск CSS-анимаций
    slide.classList.add("is-entering");
    slide.querySelectorAll("[data-scramble]").forEach(scramble);
  };

  const go = (index) => {
    active = (index + count) % count;
    render();
    enter(slides[active]);
  };

  root.classList.add("is-ready");
  controls.hidden = false;
  render();

  root.querySelector("[data-slider-prev]").addEventListener("click", () => go(active - 1));
  root.querySelector("[data-slider-next]").addEventListener("click", () => go(active + 1));

  // Клик по соседней карточке делает её активной (ссылки в ней не срабатывают)
  slides.forEach((slide, index) => {
    slide.addEventListener("click", (event) => {
      if (!slide.classList.contains("is-side")) return;
      event.preventDefault();
      event.stopPropagation(); // иначе кнопка «Заказать» в карточке сработает после активации
      go(index);
    });
  });

  root.addEventListener("keydown", (event) => {
    if (event.target.closest("input, textarea, select")) return;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      go(active - 1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      go(active + 1);
    }
  });

  // Свайп пальцем или стилусом
  let startX = null;
  root.addEventListener("pointerdown", (event) => {
    if (event.pointerType !== "mouse") startX = event.clientX;
  });
  root.addEventListener("pointerup", (event) => {
    if (startX === null) return;
    const dx = event.clientX - startX;
    startX = null;
    if (Math.abs(dx) >= SWIPE_THRESHOLD) go(dx < 0 ? active + 1 : active - 1);
  });
  root.addEventListener("pointercancel", () => {
    startX = null;
  });
}
