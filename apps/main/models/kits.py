from django.db import models

from .base import TimestampedModel


class Kit(TimestampedModel):
    """Карточка слайдера «Готовые комплекты»."""

    car_model = models.CharField("Модель авто", max_length=100, help_text="Например, JAC T9")
    protection_type = models.CharField(
        "Тип защиты", max_length=100, help_text="Например, Передняя защита"
    )
    badge = models.CharField("Метка", max_length=50, blank=True)
    spec_1 = models.CharField("Характеристика 1", max_length=150, blank=True)
    spec_2 = models.CharField("Характеристика 2", max_length=150, blank=True)
    spec_3 = models.CharField("Характеристика 3", max_length=150, blank=True)
    photo = models.ImageField("Фото", upload_to="kits/")
    is_custom = models.BooleanField(
        "Карточка «Ваша модель»",
        default=False,
        help_text="Карточка для индивидуального заказа, а не готовый комплект",
    )
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        verbose_name = "Комплект"
        verbose_name_plural = "Комплекты"
        ordering = ("order", "id")

    def __str__(self) -> str:
        return f"{self.car_model} — {self.protection_type}"

    @property
    def specs(self) -> list[str]:
        return [spec for spec in (self.spec_1, self.spec_2, self.spec_3) if spec]
