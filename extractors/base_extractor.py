# Defines the standard interface that website-specific extractors must follow.

class BaseExtractor:

    def extract_products(self, response):
        """Extract products from a webpage response."""
        raise NotImplementedError(
            "Website extractors must implement extract_products()."
        )