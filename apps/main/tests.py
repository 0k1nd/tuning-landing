import json
import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.template import Context, Template
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

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
    def test_creates_kits_once(self):
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(list(Kit.objects.values_list("code", flat=True)), ["T9", "H3"])
        kit = Kit.objects.get(code="T9")
        self.assertEqual(kit.car_model, "JAC T9")
        self.assertFalse(kit.photo)
        self.assertEqual(kit.alt, "JAC T9 в профиль с защитой бампера")


class IndexPageV4Tests(TestCase):
    def setUp(self):
        call_command("seed_demo", stdout=StringIO())

    def test_model_blocks_rendered_from_kits(self):
        html = self.client.get(reverse("main:index")).content.decode()
        self.assertIn('<p class="model__code" aria-hidden="true">T9</p>', html)
        self.assertIn('<p class="model__code" aria-hidden="true">H3</p>', html)
        self.assertIn("model--chalk", html)
        self.assertIn("model--paper", html)
        self.assertIn("[Фото JAC T9 в профиль без фона]", html)

    def test_logo_symbol_once_and_used(self):
        html = self.client.get(reverse("main:index")).content.decode()
        self.assertEqual(html.count('<symbol id="gf-logo"'), 1)
        self.assertEqual(html.count('aria-label="GRANFORT"><use href="#gf-logo"/>'), 2)

    def test_new_kit_is_one_record(self):
        Kit.objects.create(code="X5", car_model="Tank 300", part="Передняя защита", order=3)
        html = self.client.get(reverse("main:index")).content.decode()
        self.assertIn('aria-hidden="true">X5</p>', html)


class BuildImagesTests(TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.src = Path(tmp.name) / "src"
        self.out = Path(tmp.name) / "out"
        self.src.mkdir()
        Image.new("RGB", (1500, 1000), "white").save(self.src / "hero.jpg")
        photos = {"hero": {"widths": (640, 1280, 2400), "sizes": "100vw"}}
        for target in (
            "apps.main.management.commands.build_images",
            "apps.main.templatetags.photos",
        ):
            for name, value in (("OUTPUT_DIR", self.out), ("PHOTOS", photos)):
                patcher = mock.patch(f"{target}.{name}", value)
                patcher.start()
                self.addCleanup(patcher.stop)
        patcher = mock.patch("apps.main.management.commands.build_images.SOURCE_DIR", self.src)
        patcher.start()
        self.addCleanup(patcher.stop)

        from apps.main.templatetags import photos as tag_module

        tag_module._manifest.cache_clear()
        self.addCleanup(tag_module._manifest.cache_clear)

    def test_resizes_without_upscaling_and_renders_srcset(self):
        call_command("build_images", stdout=StringIO())
        self.assertEqual(
            sorted(p.name for p in self.out.glob("*.webp")), ["hero-1280.webp", "hero-640.webp"]
        )
        manifest = json.loads((self.out / "manifest.json").read_text())
        self.assertEqual(manifest["hero"], {"widths": [640, 1280], "width": 1500, "height": 1000})

        html = Template(
            '{% load photos %}{% photo "hero" "Фото" lazy=False priority=True %}'
        ).render(Context())
        self.assertIn(
            'srcset="/static/img/photos/hero-640.webp 640w, '
            '/static/img/photos/hero-1280.webp 1280w"',
            html,
        )
        self.assertIn('width="1500" height="1000"', html)
        self.assertIn('fetchpriority="high"', html)
        self.assertNotIn("loading=", html)
        self.assertNotIn("class=", html)
