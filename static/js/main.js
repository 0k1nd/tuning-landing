import { initLeadForm } from "./form.js";
import { initMenu } from "./menu.js";

const header = document.querySelector("[data-header]");
if (header) initMenu(header);

const form = document.querySelector("[data-lead-form]");
if (form) initLeadForm(form);
