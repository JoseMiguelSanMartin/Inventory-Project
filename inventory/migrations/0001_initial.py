from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InventoryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("item_name", models.CharField(max_length=100)),
                ("quantity_required", models.PositiveIntegerField(default=0)),
                ("quantity_have", models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
