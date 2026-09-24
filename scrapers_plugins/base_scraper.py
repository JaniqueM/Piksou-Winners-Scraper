from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """
    Base class for all retailer scrapers.
    """

    # True for website scrapers.
    # False for brochure/OCR scrapers.
    requires_fetcher = False

    @abstractmethod
    def extract_products(self, response=None):
        """
        Extract products from the retailer source.

        Web scrapers receive a response.

        Brochure/OCR scrapers can ignore the response.
        """
        pass