from decimal import Decimal, ROUND_HALF_UP


GBP_TO_INR_RATE = Decimal("129.00")
MONEY_PLACES = Decimal("0.01")


def gbp_to_inr(amount):
    return (Decimal(str(amount)) * GBP_TO_INR_RATE).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
