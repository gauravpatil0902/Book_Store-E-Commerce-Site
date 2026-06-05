import datetime

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def default_delivery_date():
    return django.utils.timezone.localdate() + datetime.timedelta(days=5)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, unique=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("rating", models.PositiveSmallIntegerField(default=1)),
                ("image_url", models.URLField(max_length=500)),
                ("source_url", models.URLField(blank=True, max_length=500)),
                ("in_stock", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["title"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("address", models.TextField()),
                ("payment_method", models.CharField(max_length=80)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("confirmed", "Confirmed"), ("packed", "Packed"), ("shipped", "Shipped"), ("delivered", "Delivered")], default="confirmed", max_length=20)),
                ("order_date", models.DateTimeField(auto_now_add=True)),
                ("delivery_date", models.DateField(default=default_delivery_date)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-order_date"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="store.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="store.product")),
            ],
        ),
    ]
