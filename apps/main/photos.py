"""Адаптивные фото страницы (DESIGN.md, «Изображения»: WebP + srcset).

Оригиналы лежат в assets/photos/<name>.<jpg|png|webp>. Команда `make images`
(manage.py build_images) нарезает из них static/img/photos/<name>-<ширина>.webp.
Шаблонный тег {% photo %} строит srcset из тех же ширин — списки не расходятся.
"""

from django.conf import settings

SOURCE_DIR = settings.BASE_DIR / "assets" / "photos"
OUTPUT_DIR = settings.BASE_DIR / "static" / "img" / "photos"
STATIC_PREFIX = "img/photos"

# Фото на всю ширину экрана — до 2400px (требование к главному фото в спеке)
FULL_WIDTHS = (640, 960, 1280, 1920, 2400)
# Карточки «Два исполнения» — до половины контейнера 1440px на ретине
CARD_WIDTHS = (480, 720, 960, 1200)

PHOTOS = {
    "hero": {"widths": FULL_WIDTHS, "sizes": "100vw"},
    "custom": {"widths": FULL_WIDTHS, "sizes": "100vw"},
    "variant-steel": {"widths": CARD_WIDTHS, "sizes": "(min-width: 1024px) 50vw, 100vw"},
    "variant-black": {"widths": CARD_WIDTHS, "sizes": "(min-width: 1024px) 50vw, 100vw"},
}

WEBP_QUALITY = 80


def output_name(name: str, width: int) -> str:
    return f"{name}-{width}.webp"
