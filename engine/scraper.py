# Core scraping engine responsible that is for managing the scraping process and collected products.

class ScraperEngine:
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.products = []
        self.seen_product_ids = set()