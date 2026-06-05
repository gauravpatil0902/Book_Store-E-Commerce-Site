from django import template

register = template.Library()


@register.filter
def stars(value):
    rating = int(value or 0)
    return "*" * rating + "-" * (5 - rating)


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def inr(value):
    return f"Rs. {float(value or 0):,.2f}"
