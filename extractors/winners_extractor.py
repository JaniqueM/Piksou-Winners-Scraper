# Website-specific extractor for Winners Mauritius.
# Converts Winners product HTML into standardized Product objects.


from bs4 import BeautifulSoup

from extractors.base_extractor import BaseExtractor
from models.product import Product


class WinnersExtractor(BaseExtractor):

    def extract_products(self, response):
        # Parse the HTML returned by the Winners website.
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all product cards on the page.
        product_cards = soup.select(".product-item")

        products = []

        # Process each product card.
        for card in product_cards:

            # Get the Winners product ID.
            product_id = card.get("data-productid")

            # Get the product name and URL.
            name_element = card.select_one(".product-title a")

            if name_element:
                name = name_element.get_text(strip=True)
                product_url = name_element.get("href")
            else:
                name = None
                product_url = None

            # Get the SKU.
            sku_element = card.select_one(".sku")

            if sku_element:
                sku = sku_element.get_text(strip=True)
            else:
                sku = None

            # Get the current price.
            price_element = card.select_one(".actual-price")

            if price_element:
                price = price_element.get_text(strip=True)
            else:
                price = None

            # Create a standardized Product object.
            product = Product(
                product_id=product_id,
                name=name,
                sku=sku,
                price=price,
                url=product_url,
                category=None
            )

            # Add the product to the list.
            products.append(product)

        return products