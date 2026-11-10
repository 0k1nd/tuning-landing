from __future__ import annotations

from django.contrib import admin, messages


class SingleObjectAdminMixin:
    """Разрешает создать в админке только один объект модели (настройки, singleton)."""

    def has_add_permission(self, request, obj=None):
        return not self.model._default_manager.exists()


class TimestampedAdminMixin:
    """Для моделей на базе TimestampedModel."""

    readonly_fields = ("created_at", "updated_at")
    list_filter = ("is_active",)
    actions = ("mark_active", "mark_inactive")

    @admin.action(description="Сделать активными")
    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активировано: {updated}", level=messages.SUCCESS)

    @admin.action(description="Сделать неактивными")
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано: {updated}", level=messages.SUCCESS)
