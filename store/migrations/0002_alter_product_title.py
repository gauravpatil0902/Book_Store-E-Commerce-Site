from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="title",
            field=models.CharField(max_length=255),
        ),
    ]
