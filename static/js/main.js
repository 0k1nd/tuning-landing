import { initLeadForm } from "./form.js";
import { initMenu } from "./menu.js";
import { initSlider } from "./slider.js";

const header = document.querySelector("[data-header]");
if (header) initMenu(header);

document.querySelectorAll("[data-slider]").forEach(initSlider);

const form = document.querySelector("[data-lead-form]");
if (form) initLeadForm(form);
