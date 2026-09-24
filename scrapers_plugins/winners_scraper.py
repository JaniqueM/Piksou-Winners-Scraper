# Website-specific scraper for Winners Mauritius.
#
# This plugin handles:
# 1. Winners HTML
# 2. Winners selectors
# 3. Product extraction
#
# The generic ScraperEngine handles:
# 1. Fetching pages
# 2. Categories
# 3. Pagination
# 4. Deduplication
# 5. Running the scraper


from bs4 import BeautifulSoup

from scrapers_plugins.base_scraper import BaseScraper
from models.product import Product


class WinnersExtractor(BaseScraper):

    # Winners is a website-based scraper.
    requires_fetcher = True

    # ---------------------------------------------------------
    # MAIN EXTRACTION METHOD
    # ---------------------------------------------------------

    def extract_products(self, response):

        # Parse the HTML response.
        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Find all Winners product cards.
        product_cards = soup.select(
            ".product-item"
        )

        products = []

        # Process every product card.
        for card in product_cards:

            # -------------------------------------------------
            # PRODUCT ID
            # -------------------------------------------------

            product_id = card.get(
                "data-productid"
            )

            # -------------------------------------------------
            # PRODUCT NAME + URL
            # -------------------------------------------------

            name_element = card.select_one(
                ".product-title a"
            )

            if name_element:

                name = name_element.get_text(
                    strip=True
                )

                product_url = name_element.get(
                    "href"
                )

                # Make relative URLs absolute.
                if (
                    product_url
                    and product_url.startswith("/")
                ):

                    product_url = (
                        "https://www.winners.mu"
                        + product_url
                    )

            else:

                name = None
                product_url = None

            # -------------------------------------------------
            # SKU
            # -------------------------------------------------

            sku_element = card.select_one(
                ".sku"
            )

            if sku_element:

                sku = sku_element.get_text(
                    strip=True
                )

            else:

                sku = None

            # -------------------------------------------------
            # OLD PRICE
            # -------------------------------------------------

            old_price_element = card.select_one(
                ".old-price"
            )

            if old_price_element:

                old_price = (
                    old_price_element.get_text(
                        strip=True
                    )
                )

            else:

                old_price = None

            # -------------------------------------------------
            # CURRENT PRICE
            # -------------------------------------------------

            price_element = card.select_one(
                ".actual-price"
            )

            if price_element:

                price = (
                    price_element.get_text(
                        strip=True
                    )
                )

            else:

                price = None

            # -------------------------------------------------
            # DISCOUNT
            # -------------------------------------------------

            discount_percent = None

            try:

                if old_price and price:

                    old_price_number = float(
                        old_price
                        .replace("Rs", "")
                        .replace(",", "")
                        .strip()
                    )

                    price_number = float(
                        price
                        .replace("Rs", "")
                        .replace(",", "")
                        .strip()
                    )

                    if old_price_number > 0:

                        discount_percent = round(
                            (
                                (
                                    old_price_number
                                    - price_number
                                )
                                / old_price_number
                            )
                            * 100,
                            2
                        )

            except (
                ValueError,
                TypeError
            ):

                discount_percent = None

            # -------------------------------------------------
            # PRODUCT OBJECT
            # -------------------------------------------------

            product = Product(

                product_id=product_id,

                name=name,

                sku=sku,

                price=price,

                old_price=old_price,

                discount_percent=discount_percent,

                promotion=(
                    True
                    if old_price
                    else False
                ),

                url=product_url,

                category=None,

                source="Winners Website",

                page=None
            )

            products.append(
                product
            )

        return products