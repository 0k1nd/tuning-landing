import { initLeadForm } from "./form.js";
import { initSlider } from "./slider.js";

document.querySelectorAll("[data-slider]").forEach(initSlider);

const form = document.querySelector("[data-lead-form]");
if (form) initLeadForm(form);
