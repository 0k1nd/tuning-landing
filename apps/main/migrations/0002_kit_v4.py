"""Kit под спеку v4: одна запись на модель авто вместо карточек слайдера.

Записи одной модели (передняя / задняя защита) сливаются в одну, карточка «Ваша модель» удаляется.
"""

from django.db import migrations, models


def merge_to_one_per_model(apps, schema_editor):
    Kit = apps.get_model("main", "Kit")
    Kit.objects.filter(is_custom=True).delete()

    seen = {}
    for kit in Kit.objects.order_by("order", "id"):
        if kit.car_model in seen:
            seen[kit.car_model].append(kit)
        else:
            seen[kit.car_model] = [kit]

    used_codes = set()
    for car_model, kits in seen.items():
        keep, *rest = kits
        if rest:
            keep.part = "Передняя и задняя защита"
        code = car_model.split()[-1][:10] if car_model.split() else f"M{keep.pk}"
        while code in used_codes:
            code = f"{code[:8]}{keep.pk}"[:10]
        used_codes.add(code)
        keep.code = code
        keep.save(update_fields=["code", "part"])
        Kit.objects.filter(pk__in=[k.pk for k in rest]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RenameField("kit", "protection_type", "part"),
        migrations.AddField(
            model_name="kit",
            name="code",
            field=models.CharField(default="", max_length=10, verbose_name="Код (монограмма)"),
            preserve_default=False,
        ),
        migrations.RunPython(merge_to_one_per_model, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="kit",
            name="code",
            field=models.CharField(
                help_text="Крупная надпись над фото, например T9",
                max_length=10,
                unique=True,
                verbose_name="Код (монограмма)",
            ),
        ),
        migrations.RemoveField("kit", "badge"),
        migrations.RemoveField("kit", "spec_1"),
        migrations.RemoveField("kit", "spec_2"),
        migrations.RemoveField("kit", "spec_3"),
        migrations.RemoveField("kit", "is_custom"),
        migrations.AlterField(
            model_name="kit",
            name="part",
            field=models.CharField(
                help_text="Например, Передняя и задняя защита",
                max_length=150,
                verbose_name="Тип защиты",
            ),
        ),
        migrations.AddField(
            model_name="kit",
            name="material",
            field=models.CharField(
                blank=True,
                help_text="Например, AISI 304 или чёрный металл с порошковым покрытием",
                max_length=150,
                verbose_name="Материал",
            ),
        ),
        migrations.AddField(
            model_name="kit",
            name="price",
            field=models.CharField(
                blank=True,
                help_text="Как показать на сайте: «от 45 000 ₽»",
                max_length=50,
                verbose_name="Цена",
            ),
        ),
        migrations.AlterField(
            model_name="kit",
            name="photo",
            field=models.ImageField(
                blank=True,
                help_text="PNG или WebP с прозрачным фоном, до 980px по ширине. "
                "Пока фото нет, на сайте — пунктирное место под него",
                upload_to="kits/",
                verbose_name="Фото в профиль",
            ),
        ),
        migrations.AddField(
            model_name="kit",
            name="photo_alt",
            field=models.CharField(
                blank=True,
                help_text="Пусто — «<модель> в профиль с защитой бампера»",
                max_length=200,
                verbose_name="Описание фото (alt)",
            ),
        ),
        migrations.AlterModelOptions(
            name="kit",
            options={
                "ordering": ("order", "id"),
                "verbose_name": "Комплект",
                "verbose_name_plural": "Комплекты",
            },
        ),
    ]
