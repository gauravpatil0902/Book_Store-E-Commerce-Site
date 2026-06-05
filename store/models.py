from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


def default_delivery_date():
    return timezone.localdate() + timedelta(days=5)


class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.PositiveSmallIntegerField(default=1)
    image_url = models.URLField(max_length=500)
    source_url = models.URLField(max_length=500, blank=True)
    genre = models.CharField(max_length=100, blank=True, default="")
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def mrp(self):
        return round(self.price * Decimal("1.18"), 2)


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    photo = models.FileField(upload_to="profile_photos/", blank=True)
    photo_url = models.URLField(max_length=500, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} profile"

    @property
    def full_address(self):
        parts = [self.address, self.city, self.state, self.pincode]
        return "\n".join(part for part in parts if part)

    @property
    def photo_display_url(self):
        if self.photo:
            return self.photo.url
        return self.photo_url

    @property
    def completion_percent(self):
        fields = [
            self.user.first_name,
            self.user.email,
            self.photo or self.photo_url,
            self.contact_number,
            self.address,
            self.city,
            self.state,
            self.pincode,
        ]
        filled = sum(1 for value in fields if str(value or "").strip())
        return round((filled / len(fields)) * 100)


class Order(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    address = models.TextField()
    contact_number = models.CharField(max_length=15, blank=True)
    payment_method = models.CharField(max_length=80)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField(default=default_delivery_date)

    class Meta:
        ordering = ["-order_date"]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name}, {self.city} - {self.pincode}"