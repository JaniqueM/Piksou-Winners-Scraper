# Generic brochure extractor.
# This will eventually handle product and promotion data
# extracted from retailer brochures.

from extractors.base_extractor import BaseExtractor
from models.product import Product


class BrochureExtractor(BaseExtractor):

    def extract_products(self, response):

        # Brochure extraction logic will be added here.
        products = []

        return products