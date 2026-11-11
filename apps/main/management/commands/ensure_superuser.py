import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Создаёт администратора из DJANGO_SUPERUSER_USERNAME / _PASSWORD / _EMAIL, "
        "если его ещё нет. Для Docker-окружения разработки."
    )

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")

        if not username or not password:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME/PASSWORD не заданы — пропускаю")
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Администратор {username} уже есть")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Создан администратор {username}"))
