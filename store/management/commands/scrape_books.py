from decimal import Decimal

from django.core.management.base import BaseCommand

from store.currency import gbp_to_inr
from store.models import Product
from store.scraper import fetch_catalog
from store.seed_data import SCRAPED_BOOKS


class Command(BaseCommand):
    help = "Scrape every catalogue page from books.toscrape.com and save products."

    def add_arguments(self, parser):
        parser.add_argument("--url", default="https://books.toscrape.com/")

    def handle(self, *args, **options):
        url = options["url"]
        try:
            items = fetch_catalog(url)
            source_label = "live website"
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Live scrape failed: {exc}. Using bundled scraped data."))
            items = SCRAPED_BOOKS
            source_label = "bundled fallback"

        created = 0
        updated = 0
        for item in items:
            lookup = {"source_url": item["source_url"]} if item.get("source_url") else {"title": item["title"]}
            _, was_created = Product.objects.update_or_create(
                **lookup,
                defaults={
                    "title": item["title"],
                    "price": gbp_to_inr(item["price"]),
                    "rating": int(item["rating"]),
                    "image_url": item["image_url"],
                    "source_url": item.get("source_url", url),
                    "in_stock": True,
                },
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved {len(items)} books from {source_label}. Created {created}, updated {updated}."
            )
        )
