from django.db import models

from .base import TimestampedModel


class Kit(TimestampedModel):
    """Блок модели с монограммой (DESIGN.md, «Блок модели»). Одна запись — одна модель авто."""

    code = models.CharField(
        "Код (монограмма)",
        max_length=10,
        unique=True,
        help_text="Крупная надпись над фото, например T9",
    )
    car_model = models.CharField("Модель авто", max_length=100, help_text="Например, JAC T9")
    part = models.CharField(
        "Тип защиты", max_length=150, help_text="Например, Передняя и задняя защита"
    )
    material = models.CharField(
        "Материал",
        max_length=150,
        blank=True,
        help_text="Например, AISI 304 или чёрный металл с порошковым покрытием",
    )
    price = models.CharField(
        "Цена", max_length=50, blank=True, help_text="Как показать на сайте: «от 45 000 ₽»"
    )
    photo = models.ImageField(
        "Фото в профиль",
        upload_to="kits/",
        blank=True,
        help_text="PNG или WebP с прозрачным фоном, до 980px по ширине. "
        "Пока фото нет, на сайте — пунктирное место под него",
    )
    photo_alt = models.CharField(
        "Описание фото (alt)",
        max_length=200,
        blank=True,
        help_text="Пусто — «<модель> в профиль с защитой бампера»",
    )
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        verbose_name = "Комплект"
        verbose_name_plural = "Комплекты"
        ordering = ("order", "id")

    def __str__(self) -> str:
        return f"{self.car_model} — {self.part}"

    @property
    def alt(self) -> str:
        return self.photo_alt or f"{self.car_model} в профиль с защитой бампера"
