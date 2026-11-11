from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from apps.main.models import Kit

# Фото-заглушки: --color-forest и --color-white из DESIGN.md
PLACEHOLDER_BG = "#34484A"
PLACEHOLDER_FG = "#FFFFFF"
PLACEHOLDER_SIZE = (1600, 1000)

SPECS = ("[Характеристика 1]", "[Характеристика 2]", "[Характеристика 3]")

DEMO_KITS = [
    {"car_model": "JAC T9", "protection_type": "Передняя защита"},
    {"car_model": "JAC T9", "protection_type": "Задняя защита"},
    {"car_model": "Haval H3", "protection_type": "Передняя защита"},
    {"car_model": "Haval H3", "protection_type": "Задняя защита"},
    {"car_model": "Ваша модель", "protection_type": "[Индивидуальный комплект]", "is_custom": True},
]


# Системные шрифты с кириллицей: macOS, Debian/Ubuntu, Alpine
CYRILLIC_FONTS = (
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
)
FONT_SIZE = 72


def load_font() -> tuple[ImageFont.FreeTypeFont, bool]:
    """Шрифт и признак поддержки кириллицы. Встроенный шрифт Pillow кириллицу не рисует."""
    for path in CYRILLIC_FONTS:
        try:
            return ImageFont.truetype(path, FONT_SIZE), True
        except OSError:
            continue
    return ImageFont.load_default(size=FONT_SIZE), False


def placeholder_photo(kit: Kit) -> ContentFile:
    image = Image.new("RGB", PLACEHOLDER_SIZE, PLACEHOLDER_BG)
    draw = ImageDraw.Draw(image)
    font, has_cyrillic = load_font()
    text = str(kit) if has_cyrillic else kit.car_model
    center = (PLACEHOLDER_SIZE[0] // 2, PLACEHOLDER_SIZE[1] // 2)
    draw.text(center, text, fill=PLACEHOLDER_FG, font=font, anchor="mm")
    buffer = BytesIO()
    image.save(buffer, format="WEBP", quality=80)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "Создаёт комплекты для примера: JAC T9 и Haval H3, «Ваша модель». Только для разработки."

    def handle(self, *args, **options):
        created_count = 0
        for order, data in enumerate(DEMO_KITS, start=1):
            kit, created = Kit.objects.get_or_create(
                car_model=data["car_model"],
                protection_type=data["protection_type"],
                defaults={
                    "badge": "[Метка]",
                    "spec_1": SPECS[0],
                    "spec_2": SPECS[1],
                    "spec_3": SPECS[2],
                    "is_custom": data.get("is_custom", False),
                    "order": order,
                },
            )
            if not created:
                continue
            filename = f"demo-{kit.pk}.webp"
            kit.photo.save(filename, placeholder_photo(kit), save=True)
            created_count += 1
            self.stdout.write(f"  + {kit}")

        skipped = len(DEMO_KITS) - created_count
        self.stdout.write(
            self.style.SUCCESS(f"Создано комплектов: {created_count}, уже были: {skipped}")
        )
