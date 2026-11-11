import json
from functools import cache

from django import template
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.main.photos import OUTPUT_DIR, PHOTOS, STATIC_PREFIX, output_name

register = template.Library()


@cache
def _manifest() -> dict:
    """Ширины и размеры, реально нарезанные `make images` (кешируется до перезапуска)."""
    path = OUTPUT_DIR / "manifest.json"
    return json.loads(path.read_text()) if path.exists() else {}


@register.simple_tag
def photo(name, alt, css_class="", lazy=True, priority=False):
    """<img> с srcset из static/img/photos. Пример: {% photo "hero" "Описание" lazy=False %}"""
    info = _manifest().get(name)
    if info is None:
        raise template.TemplateSyntaxError(f"Фото «{name}» не нарезано: запустите make images")

    widths = info["widths"]
    srcset = ", ".join(f"{static(f'{STATIC_PREFIX}/{output_name(name, w)}')} {w}w" for w in widths)
    # src — средняя ширина: запасной вариант для браузеров без srcset
    fallback = widths[len(widths) // 2]
    return format_html(
        '<img{} src="{}" srcset="{}" sizes="{}" width="{}" height="{}" alt="{}"{}{}>',
        format_html(' class="{}"', css_class) if css_class else "",
        static(f"{STATIC_PREFIX}/{output_name(name, fallback)}"),
        srcset,
        PHOTOS[name]["sizes"],
        info["width"],
        info["height"],
        alt,
        mark_safe(' loading="lazy"') if lazy else "",
        mark_safe(' fetchpriority="high"') if priority else "",
    )
