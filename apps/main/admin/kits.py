from django.contrib import admin
from django.utils.html import format_html

from apps.main.mixins import TimestampedAdminMixin
from apps.main.models import Kit


@admin.register(Kit)
class KitAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = (
        "photo_preview",
        "car_model",
        "protection_type",
        "badge",
        "is_custom",
        "is_active",
        "order",
    )
    list_display_links = ("photo_preview", "car_model")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "is_custom")
    search_fields = ("car_model", "protection_type")
    readonly_fields = ("photo_preview", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("car_model", "protection_type", "badge")}),
        ("Характеристики", {"fields": ("spec_1", "spec_2", "spec_3")}),
        ("Фото", {"fields": ("photo", "photo_preview")}),
        ("Отображение", {"fields": ("is_custom", "is_active", "order")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Фото")
    def photo_preview(self, obj):
        if not obj.photo:
            return "—"
        return format_html('<img src="{}" alt="" style="height:60px">', obj.photo.url)
