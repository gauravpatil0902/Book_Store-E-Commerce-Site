from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/suggestions/", views.search_suggestions, name="search_suggestions"),
    path("books/<int:product_id>/", views.product_detail, name="product_detail"),
    path("account/", views.account_view, name="account"),
    path("account/edit/", views.edit_profile_view, name="edit_profile"),
    path("signup/", views.signup_view, name="signup"),
    path("signin/", views.signin_view, name="signin"),
    path("logout/", views.logout_view, name="logout"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("cart/update/<int:product_id>/<str:action>/", views.update_cart, name="update_cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("orders/", views.orders_view, name="orders"),
    path("orders/<int:order_id>/", views.order_detail_view, name="order_detail"),
    path("orders/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
    path("set-address/", views.set_selected_address, name="set_selected_address"),
    path("address/add/", views.add_address, name="add_address"),
    path("address/delete/<int:address_id>/", views.delete_address, name="delete_address"),
]