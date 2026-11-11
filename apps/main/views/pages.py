from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from apps.main.forms import LeadForm
from apps.main.models import Kit

# Пункты меню: якоря на id секций (шапка и футер)
NAV_ITEMS = (
    ("about", "О компании"),
    ("products", "Комплекты"),
    ("benefits", "Преимущества"),
    ("custom", "Индивидуально"),
)

# Метки блока «О компании» — из спеки v4
ABOUT_BADGES = ("AISI 304", "Порошковое покрытие", "Без сверления", "Доставка по России")

# «Два исполнения» — из спеки v4; фото — заглушки до снимков заказчика
VARIANTS = (
    {
        "title": "Нержавеющая сталь AISI 304",
        "text": "Зеркальная полировка",
        "photo": "variant-steel",
        "alt": "[Защита бампера из нержавеющей стали AISI 304 с зеркальной полировкой]",
    },
    {
        "title": "Чёрный металл",
        "text": "Порошковое покрытие",
        "photo": "variant-black",
        "alt": "[Защита бампера из чёрного металла с порошковым покрытием]",
    },
)

# «Почему GRANFORT»: 6 пунктов из задания; описания ждут текстов заказчика
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
        context.update(
            {
                "meta_title": "GRANFORT — защита бамперов для китайских внедорожников",
                "nav_items": NAV_ITEMS,
                "about_badges": ABOUT_BADGES,
                "variants": VARIANTS,
                "benefits": BENEFITS,
                "kits": Kit.objects.filter(is_active=True),
                "lead_form": LeadForm(initial={"source": "contacts"}),
            }
        )
        return context
