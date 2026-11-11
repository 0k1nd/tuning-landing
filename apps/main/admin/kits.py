from django.contrib import admin
from django.utils.html import format_html

from apps.main.mixins import TimestampedAdminMixin
from apps.main.models import Kit


@admin.register(Kit)
class KitAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ("photo_preview", "code", "car_model", "part", "price", "is_active", "order")
    list_display_links = ("photo_preview", "code", "car_model")
    list_editable = ("order", "is_active")
    search_fields = ("code", "car_model", "part")
    readonly_fields = ("photo_preview", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("code", "car_model", "part", "material", "price")}),
        ("Фото", {"fields": ("photo", "photo_alt", "photo_preview")}),
        ("Отображение", {"fields": ("is_active", "order")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Фото")
    def photo_preview(self, obj):
        if not obj.photo:
            return "—"
        return format_html('<img src="{}" alt="" style="height:60px">', obj.photo.url)
