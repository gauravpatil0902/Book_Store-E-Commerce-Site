from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0004_alter_order_delivery_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerprofile",
            name="photo_url",
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
