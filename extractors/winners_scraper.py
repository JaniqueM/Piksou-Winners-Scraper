# Website-specific scraper for Winners Mauritius.
# This plugin handles:
#1. Winners HTML
#2. Winners selectors
#3. Product extraction

from bs4 import BeautifulSoup

from extractors.base_extractor import BaseExtractor
from models.product import Product


class WinnersExtractor(BaseExtractor):

    #Winners is a website-based extractor.
    requires_fetcher = True

    def extract_products(self, response):

        #Parse the HTML response.
        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        #Find all Winners product cards.
        product_cards = soup.select(
            ".product-item"
        )

        products = []

        #Process every product card.
        for card in product_cards:

            #PRODUCT ID
            product_id = card.get(
                "data-productid"
            )

            #PRODUCT NAME + URL
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

            else:

                name = None
                product_url = None

            #SKU
            sku_element = card.select_one(
                ".sku"
            )

            if sku_element:

                sku = sku_element.get_text(
                    strip=True
                )

            else:

                sku = None

            #OLD PRICE
            old_price_element = card.select_one(
                ".old-price"
            )

            if old_price_element:

                old_price = old_price_element.get_text(
                    strip=True
                )

            else:

                old_price = None

            #CURRENT PRICE
            price_element = card.select_one(
                ".actual-price"
            )

            if price_element:

                price = price_element.get_text(
                    strip=True
                )

            else:

                price = None

            #DISCOUNT
            discount_percent = None

            # Try to convert prices into numbers.
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

            except (ValueError, TypeError):

                discount_percent = None

            #PRODUCT OBJECT
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

            #Add Product object.
            products.append(product)

        return products