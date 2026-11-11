from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from apps.main.forms import LeadForm
from apps.main.models import Kit

# Пункты меню: якоря на id секций (шапка и футер)
NAV_ITEMS = (
    ("about", "О компании"),
    ("products", "Продукция"),
    ("benefits", "Преимущества"),
    ("custom", "Индивидуально"),
)

# Темы преимуществ — из спецификации; описания ждут текстов заказчика
BENEFITS = (
    "Материалы",
    "Без сверления",
    "Комплект или под ключ",
    "Под вашу модель",
    "Доставка по России",
    "Специализация на китайских авто",
)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kits = list(Kit.objects.filter(is_active=True))
        context.update(
            {
                "meta_title": "Защита бамперов для китайских внедорожников — [Название]",
                "nav_items": NAV_ITEMS,
                "benefits": BENEFITS,
                "kits": kits,
                "ready_kits": [kit for kit in kits if not kit.is_custom],
                "lead_form": LeadForm(initial={"source": "contacts"}),
            }
        )
        return context
