from django.contrib import admin

from apps.main.models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "phone", "car_model", "status", "source")
    list_editable = ("status",)
    list_filter = ("status", "source", "created_at")
    search_fields = ("name", "phone", "car_model")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("name", "phone", "car_model")}),
        ("Обработка", {"fields": ("status", "source")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )
