from django.db import models

from .validators import phone_validator


class Lead(models.Model):
    """Заявка из формы обратной связи."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Обработана"
        REJECTED = "rejected", "Отклонена"

    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=12, validators=[phone_validator])
    car_model = models.CharField("Модель автомобиля", max_length=100, blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW, db_index=True
    )
    source = models.CharField(
        "Источник",
        max_length=50,
        blank=True,
        help_text="Откуда отправлена заявка: блок или кнопка на странице",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name}, {self.phone}"
