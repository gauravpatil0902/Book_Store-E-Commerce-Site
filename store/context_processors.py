from decimal import Decimal

from .models import CustomerProfile, Product


def cart_summary(request):
    cart = request.session.get("cart", {})
    count = sum(cart.values())
    subtotal = Decimal("0.00")

    if cart:
        products = Product.objects.filter(id__in=cart.keys())
        for product in products:
            subtotal += product.price * cart[str(product.id)]

    context = {"cart_count": count, "cart_subtotal": subtotal}

    if request.user.is_authenticated:
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        context["nav_profile"] = profile
        context["profile_completion"] = profile.completion_percent
    else:
        context["profile_completion"] = 0

    return context
