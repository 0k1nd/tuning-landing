from django.core.management.base import BaseCommand

from apps.main.models import Kit

# Готовые комплекты из спеки v4. Фото нет — на сайте пунктирное место под него.
DEMO_KITS = [
    {"code": "T9", "car_model": "JAC T9"},
    {"code": "H3", "car_model": "Haval H3"},
]

DEFAULTS = {
    "part": "Передняя и задняя защита",
    "material": "AISI 304 или чёрный металл с порошковым покрытием",
    "price": "[от … ₽]",
}


class Command(BaseCommand):
    help = "Создаёт комплекты для примера: JAC T9 и Haval H3. Только для разработки."

    def handle(self, *args, **options):
        created_count = 0
        for order, data in enumerate(DEMO_KITS, start=1):
            kit, created = Kit.objects.get_or_create(
                code=data["code"],
                defaults={"car_model": data["car_model"], "order": order, **DEFAULTS},
            )
            if created:
                created_count += 1
                self.stdout.write(f"  + {kit}")

        skipped = len(DEMO_KITS) - created_count
        self.stdout.write(
            self.style.SUCCESS(f"Создано комплектов: {created_count}, уже были: {skipped}")
        )
