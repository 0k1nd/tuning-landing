// prefers-reduced-motion: проверяется в момент вызова, чтобы учесть смену настройки на лету
const query = window.matchMedia("(prefers-reduced-motion: reduce)");

export function prefersReducedMotion() {
  return query.matches;
}
