# Core scraping engine responsible for managing
# categories, pages, and collected products.


class ScraperEngine:

    def __init__(self, fetcher, config):
        # Stores the Fetcher used to send HTTP requests.
        self.fetcher = fetcher

        # Stores the scraper configuration.
        self.config = config

        # Stores all collected products.
        self.products = []

        # Keeps track of products already collected.
        self.seen_product_ids = set()

    def fetch_page(self, url):
        # Fetches a webpage using the configured Fetcher.
        return self.fetcher.get(url)

    def build_page_url(self, category_path, page):
        # Builds the URL for a specific category and page.
        return (
            f"{self.config.base_url}"
            f"{category_path}"
            f"{self.config.page_url_template.format(page=page)}"
        )

    def add_products(self, products):
        # Adds products while preventing duplicates.
        for product in products:

            product_id = product.product_id

            # Skip products that have already been collected.
            if product_id in self.seen_product_ids:
                continue

            # Record the product ID.
            self.seen_product_ids.add(product_id)

            # Store the product.
            self.products.append(product)

    def scrape_category(self, category_path, extractor):
        # Scrapes all pages within one category.

        page = self.config.start_page

        while page <= self.config.max_pages:

            # Build the URL for this category and page.
            page_url = self.build_page_url(
                category_path,
                page
            )

            # Fetch the page.
            response = self.fetch_page(page_url)

            # Stop if the request failed.
            if response is None:
                break

            # Extract products from the page.
            products = extractor.extract_products(response)

            # Stop when no products are found.
            if not products:
                break

            # Add products while removing duplicates.
            self.add_products(products)

            print(
                f"Fetched category {category_path} "
                f"page {page}: {len(products)} products"
            )

            page += 1

    def scrape(self, extractor):
        # Scrapes every configured category.

        for category_path in self.config.category_paths:

            print(f"\nStarting category: {category_path}")

            self.scrape_category(
                category_path,
                extractor
            )

        # Return all unique products.
        return self.products