# Website-specific extractor for Kingsavers.
# This plugin converts Kingsavers product HTML
# into standardized Product objects.


from bs4 import BeautifulSoup

from extractors.base_extractor import BaseExtractor
from models.product import Product


class KingsaversExtractor(BaseExtractor):

    def extract_products(self, response):

        # Parse the Kingsavers webpage.
        soup = BeautifulSoup(response.text, "html.parser")

        # We will add the Kingsavers-specific
        # product selectors after inspecting the website.

        products = []

        return products