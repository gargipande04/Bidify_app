from django.db import migrations

from api.categories import CATEGORY_TREE


def seed_categories(apps, schema_editor):
    Category = apps.get_model("api", "Category")

    for group in CATEGORY_TREE:
        parent, _ = Category.objects.get_or_create(name=group["name"], parent=None)
        for child_name in group["children"]:
            Category.objects.get_or_create(name=child_name, parent=parent)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0006_favoriteitem"),
    ]

    operations = [
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
