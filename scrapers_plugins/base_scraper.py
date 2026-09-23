#Defines the standard interface that all PikSou scrapers must follow.

class BaseExtractor:

    #Web-based scraper need the generic Fetcher.
    #Brochure/OCR extractors can set this to False.
    requires_fetcher = True

    def extract_products(self, response=None):
        """
        Extract products and return a list of Product objects.

        Web extractors receive an HTTP response.
        Brochure extractors can ignore the response and process
        their own source files.
        """
        raise NotImplementedError(
            "Extractors must implement extract_products()."
        )