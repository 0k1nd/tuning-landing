import shutil
import tempfile
from io import StringIO

from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.main.forms import LeadForm
from apps.main.models import Kit, Lead, SiteSettings


class LeadFormPhoneTests(TestCase):
    def clean_phone(self, raw):
        form = LeadForm(data={"name": "Иван", "phone": raw})
        form.is_valid()
        return form.cleaned_data.get("phone"), form.errors.get("phone")

    def test_normalizes_common_formats(self):
        for raw in ("+7 (999) 123-45-67", "89991234567", "79991234567", "9991234567"):
            with self.subTest(raw=raw):
                self.assertEqual(self.clean_phone(raw), ("+79991234567", None))

    def test_rejects_wrong_length(self):
        for raw in ("+7 999 123", "+1 (999) 123-45-67-8"):
            with self.subTest(raw=raw):
                phone, errors = self.clean_phone(raw)
                self.assertIsNone(phone)
                self.assertTrue(errors)

    def test_blank_name_is_required(self):
        form = LeadForm(data={"name": "   ", "phone": "+79991234567"})
        self.assertIn("name", form.errors)


class LeadCreateViewTests(TestCase):
    url = reverse("main:lead_create")

    def test_valid_lead_is_saved(self):
        response = self.client.post(
            self.url,
            {"name": "Иван", "phone": "8 999 123-45-67", "car_model": "JAC T9", "source": "hero"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"ok": True})
        lead = Lead.objects.get()
        self.assertEqual(lead.phone, "+79991234567")
        self.assertEqual(lead.status, Lead.Status.NEW)
        self.assertEqual(lead.source, "hero")

    def test_valid_lead_is_logged_after_commit(self):
        with self.assertLogs("apps.main.notifications", level="INFO") as logs:
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(self.url, {"name": "Иван", "phone": "+79991234567"})
        self.assertIn("Новая заявка", logs.output[0])
        self.assertIn("+79991234567", logs.output[0])

    def test_invalid_lead_returns_field_errors(self):
        response = self.client.post(self.url, {"name": "", "phone": "123"})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["ok"])
        self.assertEqual(set(data["errors"]), {"name", "phone"})
        self.assertFalse(Lead.objects.exists())

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, {"name": "Иван", "phone": "+79991234567"})
        self.assertEqual(response.status_code, 403)

    def test_csrf_token_from_index_page_works(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("main:index"))
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.url,
            {"name": "Иван", "phone": "+79991234567"},
            headers={"X-CSRFToken": token},
        )
        self.assertEqual(response.status_code, 201)


class IndexViewTests(TestCase):
    def test_context(self):
        response = self.client.get(reverse("main:index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("kits", response.context)
        self.assertIsInstance(response.context["lead_form"], LeadForm)
        self.assertIsInstance(response.context["site_settings"], SiteSettings)


class SiteSettingsTests(TestCase):
    def test_singleton(self):
        SiteSettings(phone="+79991234567").save()
        SiteSettings(phone="+70000000000").save()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.load().phone_display, "+7 (000) 000-00-00")


class SeedDemoCommandTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media_root)

    def test_creates_kits_once(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            call_command("seed_demo", stdout=StringIO())
            call_command("seed_demo", stdout=StringIO())
            self.assertEqual(Kit.objects.count(), 5)
            self.assertEqual(Kit.objects.filter(is_custom=True).count(), 1)
            kit = Kit.objects.first()
            self.assertTrue(kit.photo.name.endswith(".webp"))
            self.assertEqual(len(kit.specs), 3)
