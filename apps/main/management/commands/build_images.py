import json

from django.core.management.base import BaseCommand, CommandError
from PIL import Image

from apps.main.photos import OUTPUT_DIR, PHOTOS, SOURCE_DIR, WEBP_QUALITY, output_name

SOURCE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def find_source(name: str):
    for ext in SOURCE_EXTENSIONS:
        path = SOURCE_DIR / f"{name}{ext}"
        if path.exists():
            return path
    return None


class Command(BaseCommand):
    help = "Нарезает фото из assets/photos в static/img/photos: WebP нужных ширин для srcset."

    def handle(self, *args, **options):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        manifest = {}
        missing = []

        for name, config in PHOTOS.items():
            source = find_source(name)
            if source is None:
                missing.append(name)
                continue

            with Image.open(source) as original:
                image = original.convert("RGBA" if original.mode in ("RGBA", "LA", "P") else "RGB")
                src_w, src_h = image.size
                # Не увеличиваем: ширины больше оригинала пропускаем
                widths = [w for w in config["widths"] if w <= src_w] or [src_w]
                for width in widths:
                    height = round(src_h * width / src_w)
                    resized = image.resize((width, height), Image.Resampling.LANCZOS)
                    resized.save(
                        OUTPUT_DIR / output_name(name, width), "WEBP", quality=WEBP_QUALITY
                    )

            manifest[name] = {"widths": widths, "width": src_w, "height": src_h}
            sizes_kb = ", ".join(
                f"{w}px {round((OUTPUT_DIR / output_name(name, w)).stat().st_size / 1024)} КБ"
                for w in widths
            )
            self.stdout.write(f"  {name}: {sizes_kb}")

        (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

        if missing:
            raise CommandError(f"Нет оригиналов в {SOURCE_DIR}: {', '.join(missing)}")
        self.stdout.write(self.style.SUCCESS(f"Готово: {len(manifest)} фото → {OUTPUT_DIR}"))
