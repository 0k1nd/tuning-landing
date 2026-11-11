from django.contrib import admin

from apps.main.mixins import SingleObjectAdminMixin
from apps.main.models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingleObjectAdminMixin, admin.ModelAdmin):
    list_display = ("__str__", "phone", "email", "updated_at")
    readonly_fields = ("updated_at",)

    fieldsets = (
        ("Связь", {"fields": ("phone", "email", "vk_url", "address")}),
        ("Заявки", {"fields": ("response_time",)}),
        ("Служебное", {"fields": ("updated_at",)}),
    )

    def has_delete_permission(self, request, obj=None):
        return False
