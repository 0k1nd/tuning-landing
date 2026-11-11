from django.db import models

from .validators import phone_validator


class SiteSettings(models.Model):
    """Контакты компании. Единственная запись (pk=1)."""

    phone = models.CharField("Телефон", max_length=12, blank=True, validators=[phone_validator])
    email = models.EmailField("Почта", blank=True)
    vk_url = models.URLField("ВКонтакте", blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    response_time = models.CharField(
        "Срок ответа на заявку",
        max_length=100,
        blank=True,
        help_text="Показывается в окне успешной отправки, например «в течение 30 минут»",
    )
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Контакты компании"
        verbose_name_plural = "Контакты компании"

    def __str__(self) -> str:
        return "Контакты компании"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def phone_display(self) -> str:
        """+79991234567 → +7 (999) 123-45-67."""
        p = self.phone
        if len(p) != 12:
            return p
        return f"+7 ({p[2:5]}) {p[5:8]}-{p[8:10]}-{p[10:12]}"
