from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(auto_now=True, db_index=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Активен")

    class Meta:
        abstract = True
        ordering = ("-created_at",)
