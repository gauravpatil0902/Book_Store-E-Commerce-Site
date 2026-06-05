from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CheckoutForm, ProfileForm, SignUpForm, AddressForm
from .models import CustomerProfile, Order, OrderItem, Product, Address
from .services import ensure_products


def _cart(request):
    return request.session.setdefault("cart", {})


def _cart_products(request):
    cart = _cart(request)
    products = Product.objects.filter(id__in=cart.keys())
    lines = []
    subtotal = Decimal("0.00")
    total_quantity = 0

    for product in products:
        quantity = cart[str(product.id)]
        line_total = product.price * quantity
        subtotal += line_total
        total_quantity += quantity
        lines.append({"product": product, "quantity": quantity, "line_total": line_total})

    delivery = Decimal("0.00") if subtotal >= Decimal("999.00") or subtotal == 0 else Decimal("99.00")
    return lines, subtotal, delivery, subtotal + delivery, total_quantity


def _profile_for(user):
    profile, _ = CustomerProfile.objects.get_or_create(user=user)
    return profile


def _get_address_context(request):
    user_addresses = []
    selected_address = None
    if request.user.is_authenticated:
        user_addresses = list(Address.objects.filter(user=request.user))
        selected_id = request.session.get('selected_address_id')
        if selected_id:
            selected_address = next((a for a in user_addresses if a.id == int(selected_id)), None)
        if not selected_address and user_addresses:
            selected_address = next((a for a in user_addresses if a.is_default), user_addresses[0])
    return user_addresses, selected_address


def home(request):
    ensure_products()
    user_addresses, selected_address = _get_address_context(request)
    products = Product.objects.all()
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    sort = request.GET.get("sort", "featured")
    max_price = request.GET.get("max_price", "8000")

    if query:
        products = products.filter(Q(title__icontains=query))
    if category:
        products = products.filter(genre__iexact=category)
    if max_price:
        products = products.filter(price__lte=max_price)
    if sort == "price-low":
        products = products.order_by("price")
    elif sort == "price-high":
        products = products.order_by("-price")
    elif sort == "rating":
        products = products.order_by("-rating", "title")

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(request, "store/home.html", {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "querystring": query_params.urlencode(),
        "total_products": paginator.count,
        "query": query,
        "category": category,
        "sort": sort,
        "max_price": max_price,
        "user_addresses": user_addresses,
        "selected_address": selected_address,
    })


def search_suggestions(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(title__icontains=query).order_by("title")[:8]

    return JsonResponse({
        "results": [
            {
                "title": product.title,
                "price": f"Rs. {float(product.price):,.2f}",
                "image_url": product.image_url,
                "url": reverse("product_detail", args=[product.id]),
            }
            for product in products
        ]
    })


def set_selected_address(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['selected_address_id'] = data['address_id']
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def add_address(request):
    form = AddressForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        if form.cleaned_data.get('is_default'):
            Address.objects.filter(user=request.user).update(is_default=False)
        address.save()
        messages.success(request, "Address added successfully.")
        return redirect('account')
    return render(request, 'store/add_address.html', {'form': form})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    if str(request.session.get('selected_address_id')) == str(address_id):
        del request.session['selected_address_id']
    messages.success(request, "Address removed.")
    return redirect('account')


@login_required
def account_view(request):
    user_addresses, selected_address = _get_address_context(request)
    profile = _profile_for(request.user)
    return render(request, "store/account.html", {
        "profile": profile,
        "user_addresses": user_addresses,
        "selected_address": selected_address,
    })


@login_required
def edit_profile_view(request):
    profile = _profile_for(request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your account information was updated.")
        return redirect("account")
    return render(request, "store/edit_profile.html", {"form": form})


def product_detail(request, product_id):
    user_addresses, selected_address = _get_address_context(request)
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.exclude(id=product.id).filter(rating__gte=product.rating)[:4]
    return render(request, "store/product_detail.html", {
        "product": product,
        "related_products": related_products,
        "user_addresses": user_addresses,
        "selected_address": selected_address,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account Created. Now You Can Buy What You Want!")
        return redirect("home")
    return render(request, "store/auth.html", {"form": form, "mode": "signup"})


def signin_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
        login(request, user)
        messages.success(request, "Sign in successful.")
        return redirect("home")
    return render(request, "store/auth.html", {"form": form, "mode": "signin"})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("home")


def add_to_cart(request, product_id):
    get_object_or_404(Product, id=product_id)
    cart = _cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    request.session.modified = True
    messages.success(request, "Book added to your cart.")
    next_url = request.POST.get("next") or "cart"
    return redirect(next_url)


def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.session["cart"] = {str(product.id): 1}
    request.session.modified = True
    messages.success(request, "Ready for checkout. Confirm your details to place the order.")
    return redirect("checkout")


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ["confirmed", "packed"]:
        order.status = "cancelled"
        order.save()
        messages.success(request, "Your order has been cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled as it has already been shipped.")
    return redirect("order_detail", order_id=order.id)


def update_cart(request, product_id, action):
    cart = _cart(request)
    key = str(product_id)

    if key in cart:
        if action == "inc":
            cart[key] += 1
        elif action == "dec":
            cart[key] -= 1
        elif action == "remove":
            cart.pop(key, None)
        if cart.get(key, 0) <= 0:
            cart.pop(key, None)

    request.session.modified = True

    selected_ids = request.GET.getlist("selected_ids")
    if selected_ids:
        qs = "&".join(f"selected_ids={sid}" for sid in selected_ids)
        return redirect(f"{reverse('cart')}?{qs}")
    return redirect("cart")


def cart_view(request):
    user_addresses, selected_address = _get_address_context(request)
    lines, subtotal, delivery, total, total_quantity = _cart_products(request)
    preselected_ids = request.GET.getlist("selected_ids")
    return render(request, "store/cart.html", {
        "lines": lines,
        "subtotal": subtotal,
        "delivery": delivery,
        "total": total,
        "total_quantity": total_quantity,
        "preselected_ids": preselected_ids,
        "user_addresses": user_addresses,
        "selected_address": selected_address,
    })


@login_required
def checkout_view(request):
    user_addresses, selected_address = _get_address_context(request)
    lines, subtotal, delivery, total, total_quantity = _cart_products(request)
    if not lines:
        messages.info(request, "Add books to your cart before checkout.")
        return redirect("cart")

    profile = _profile_for(request.user)
    initial = {
        "contact_number": profile.contact_number,
        "address": profile.full_address,
        "payment_amount": total,
    }
    form = CheckoutForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["payment_amount"] != total:
            form.add_error("payment_amount", f"Enter the exact order total: Rs. {total:,.2f}.")
        else:
            with transaction.atomic():
                profile.contact_number = form.cleaned_data["contact_number"]
                profile.address = form.cleaned_data["address"]
                profile.city = ""
                profile.state = ""
                profile.pincode = ""
                profile.save(update_fields=["contact_number", "address", "city", "state", "pincode"])
                order = Order.objects.create(
                    user=request.user,
                    address=form.cleaned_data["address"],
                    contact_number=form.cleaned_data["contact_number"],
                    payment_method=form.cleaned_data["payment_method"],
                    total=total,
                )
                for line in lines:
                    OrderItem.objects.create(
                        order=order,
                        product=line["product"],
                        quantity=line["quantity"],
                        price=line["product"].price,
                    )
            request.session["cart"] = {}
            messages.success(request, "Order placed successfully.")
            return redirect(f"{reverse('order_detail', args=[order.id])}?order_success=1")
    return render(request, "store/checkout.html", {
        "form": form,
        "lines": lines,
        "subtotal": subtotal,
        "delivery": delivery,
        "total": total,
        "total_quantity": total_quantity,
        "user_addresses": user_addresses,
        "selected_address": selected_address,
    })


@login_required
def orders_view(request):
    orders = request.user.orders.prefetch_related("items__product")
    return render(request, "store/orders.html", {"orders": orders})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})