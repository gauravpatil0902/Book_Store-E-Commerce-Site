from .currency import gbp_to_inr
from .models import Product
from .scraper import fetch_catalog
from .seed_data import SCRAPED_BOOKS


def ensure_products():
    if Product.objects.exists():
        return

    try:
        items = fetch_catalog()
    except Exception:
        items = SCRAPED_BOOKS

    for item in items:
        Product.objects.create(
            title=item["title"],
            price=gbp_to_inr(item["price"]),
            rating=item["rating"],
            image_url=item["image_url"],
            source_url=item.get("source_url", "https://books.toscrape.com/"),
            genre=item.get("genre", ""),
        )