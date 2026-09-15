# This is the core scraping engine that is responsible for managing
# the scraping process and collecting products.

class ScraperEngine:

    def __init__(self, fetcher, config):
        # Stores the Fetcher responsible for sending HTTP requests.
        self.fetcher = fetcher

        # Stores the scraper configuration.
        self.config = config

        # Stores all products collected by the scraper.
        self.products = []

        # Keeps track of product IDs that have already been collected.
        # This prevents duplicate products.
        self.seen_product_ids = set()

    def fetch_page(self, url):
        # Fetches a webpage using the configured Fetcher.
        return self.fetcher.get(url)

    def build_page_url(self, page):
        # Builds the URL for a specific page using the
        # pagination pattern defined in the configuration.
        return f"{self.config.base_url}{self.config.page_url_template.format(page=page)}"

    def add_products(self, products):
        # Adds products to the collection while preventing duplicates.
        for product in products:

            # Gets the unique product ID.
            product_id = product.product_id

            # Skip the product if it has already been collected.
            if product_id in self.seen_product_ids:
                continue

            # Record the product ID so it cannot be added again.
            self.seen_product_ids.add(product_id)

            # Add the product to the main product collection.
            self.products.append(product)

    def scrape_pages(self, extractor):
        # Loops through pages until there are no more products
        # or the maximum page limit is reached.

        page = self.config.start_page

        while page <= self.config.max_pages:

            # Build the URL for the current page.
            page_url = self.build_page_url(page)

            # Fetch the webpage.
            response = self.fetch_page(page_url)

            # Stop scraping if the request failed.
            if response is None:
                break

            # Use the website-specific extractor to extract products.
            products = extractor.extract_products(response)

            # Stop when no products are found on the page.
            if not products:
                break

            # Add the extracted products to the collection.
            self.add_products(products)

            # Display progress in the terminal.
            print(f"Fetched page {page}: {page_url}")
            print(f"Products found on page: {len(products)}")

            # Move to the next page.
            page += 1

        # Return all unique products collected by the engine.
        return self.products