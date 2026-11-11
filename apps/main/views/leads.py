from django.http import JsonResponse
from django.views import View

from apps.main.forms import LeadForm


class LeadCreateView(View):
    """Приём заявки через fetch: ответ JSON, ошибки по полям."""

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        form = LeadForm(request.POST)
        if not form.is_valid():
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({"ok": False, "errors": errors}, status=400)
        form.save()
        return JsonResponse({"ok": True}, status=201)
