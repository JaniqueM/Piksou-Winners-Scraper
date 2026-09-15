# This is the core scraping engine that is responsible for managing the scraping process and collected products.


class ScraperEngine:
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.products = []
        self.seen_product_ids = set()

    def fetch_page(self, url):
        # Fetches a webpage using the configured fetcher.
        # This is in the ScraperEngine as it uses the fetcher class.
        return self.fetcher.get(url)

    def build_page_url(self, base_url, page):
        # Build a page URL using the configured pagination format.
        return f"{base_url}?pagenumber={page}"

    def add_products(self, products):
        # Add products while preventing duplicates.
        for product in products:
            product_id = product.product_id

            if product_id in self.seen_product_ids:
                continue

            self.seen_product_ids.add(product_id)
            self.products.append(product)

    def scrape_pages(self, base_url, extract_products, start_page=1):
        # Loop through pages until no more products are found.
        page = start_page

        while True:
            page_url = self.build_page_url(base_url, page)

            response = self.fetch_page(page_url)

            if response is None:
                break

            products = extract_products(response)

            if not products:
                break

            self.add_products(products)

            print(f"Fetched page {page}: {page_url}")

            page += 1

        return self.products