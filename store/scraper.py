import html
import re
from urllib.parse import urljoin
from urllib.request import urlopen


RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def fetch_catalog(start_url="https://books.toscrape.com/", timeout=20):
    books = []
    seen_urls = set()

    # First get all category URLs from homepage
    with urlopen(start_url, timeout=timeout) as response:
        source = response.read().decode("utf-8", errors="ignore")

    category_urls = find_category_urls(source, start_url)

    for cat_url, genre in category_urls:
        current_url = cat_url
        while current_url and current_url not in seen_urls:
            seen_urls.add(current_url)
            with urlopen(current_url, timeout=timeout) as response:
                cat_source = response.read().decode("utf-8", errors="ignore")
            books.extend(parse_items(cat_source, current_url, genre))
            current_url = find_next_url(cat_source, current_url)

    return books


def find_category_urls(source, base_url):
    categories = []
    for match in re.finditer(r'<a href="catalogue/category/books/([^"]+)"', source):
        path = match.group(1)
        genre = path.split("_")[0].replace("-", " ").title()
        full_url = urljoin(base_url, f"catalogue/category/books/{path}")
        categories.append((full_url, genre))
    return categories


def parse_items(source, base_url, genre=""):
    products = []
    for match in re.finditer(r'<article class="product_pod">(?P<body>[\s\S]*?)</article>', source):
        body = match.group("body")
        title_match = re.search(r'title="(?P<title>[^"]+)"', body)
        link_match = re.search(r'<h3>\s*<a href="(?P<link>[^"]+)"', body)
        image_match = re.search(r'<img src="(?P<image>[^"]+)"', body)
        price_match = re.search(r'price_color">[^0-9]*(?P<price>[0-9.]+)', body)
        rating_match = re.search(r"star-rating (?P<rating>\w+)", body)
        if not all([title_match, link_match, image_match, price_match, rating_match]):
            continue

        products.append(
            {
                "title": html.unescape(title_match.group("title")),
                "price": price_match.group("price"),
                "rating": RATING_MAP.get(rating_match.group("rating"), 1),
                "image_url": urljoin(base_url, image_match.group("image")),
                "source_url": urljoin(base_url, link_match.group("link")),
                "genre": genre,
            }
        )
    return products


def find_next_url(source, base_url):
    next_match = re.search(r'<li class="next">\s*<a href="(?P<url>[^"]+)"', source)
    if not next_match:
        return None
    return urljoin(base_url, next_match.group("url"))