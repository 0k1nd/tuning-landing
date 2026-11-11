from apps.main.models import SiteSettings


def site_settings(request):
    """Контакты компании во всех шаблонах: шапка, блок контактов, футер, модалки."""
    return {"site_settings": SiteSettings.load()}
