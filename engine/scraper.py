# Core scraping engine responsible that is for managing the scraping process and collected products.

class ScraperEngine:
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.products = []
        self.seen_product_ids = set()

        def fetch_page(self, url):
        #Fetch a webpage using the fetcher.py
            return self.fetcher.get(url)

    def scrape_pages(self, base_url, start_page=1):
        #Loop through pages until no more products are found.
        page = start_page

        while True:
            page_url = f"{base_url}?pagenumber={page}"

            response = self.fetch_page(page_url)

            if response is None:
                break

            # This will later be replaced by the adapter's extraction logic.
            print(f"Fetched page {page}: {page_url}")

            page += 1