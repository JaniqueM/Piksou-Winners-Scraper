# Core scraping engine responsible for running
# independent retailer scrapers and collecting products.

class ScraperEngine:

    def __init__(self, fetcher=None, config=None, extractor=None):

        # Optional reusable HTTP fetcher.
        self.fetcher = fetcher

        # Optional configuration for website scraping.
        self.config = config

        # The retailer scraper/plugin being used.
        self.extractor = extractor

        # Stores all collected products.
        self.products = []

        # Keeps record of products already collected.
        self.seen_product_ids = set()

    # WEB FETCHING
    def fetch_page(self, url):
        """
        Fetch a webpage using the configured Fetcher.
        """

        if self.fetcher is None:
            raise ValueError(
                "A Fetcher is required for web-based extractors."
            )

        return self.fetcher.get(url)

    # URL BUILDING
    def build_page_url(self, category_path, page):
        """
        Builds the URL for a specific category and page.
        """

        if self.config is None:
            raise ValueError(
                "ScraperConfig is required for web-based scraping."
            )

        return (
            f"{self.config.base_url}"
            f"{category_path}"
            f"{self.config.page_url_template.format(page=page)}"
        )
    
    # PRODUCT STORAGE
    def add_products(self, products):
        """
        Adds products while preventing duplicates.

        Products with a product_id use that ID.

        Products without a product_id use a combination
        of name, price, old price, and source.
        """

        for product in products:

            # Use product ID when available.
            if product.product_id is not None:

                unique_key = (
                    "id",
                    product.product_id
                )

            else:

                # Brochure/OCR products may not have product IDs.
                unique_key = (
                    "product",
                    product.source,
                    product.name,
                    product.price,
                    product.old_price
                )

            # Skip duplicates.
            if unique_key in self.seen_product_ids:
                continue

            # Record product.
            self.seen_product_ids.add(unique_key)

            # Store product.
            self.products.append(product)

    # WEB CATEGORY SCRAPING
    def scrape_category(self, category_path):
        """
        Scrapes all pages within one website category.

        Used by web-based scrapers such as Winners.
        """

        if self.config is None:
            raise ValueError(
                "ScraperConfig is required for category scraping."
            )

        page = self.config.start_page

        while page <= self.config.max_pages:

            # Build URL.
            page_url = self.build_page_url(
                category_path,
                page
            )

            print(
                f"Fetching {page_url}"
            )

            # Fetch page.
            response = self.fetch_page(page_url)

            # Stop if request failed.
            if response is None:
                break

            # Extract products using selected scraper.
            products = self.extractor.extract_products(response)

            # Stop when no products are found.
            if not products:
                break

            # Add products.
            self.add_products(products)

            print(
                f"Fetched category {category_path} "
                f"page {page}: {len(products)} products"
            )

            page += 1

    # WEB SCRAPER
    def run_web_extractor(self):
        """
        Runs a web-based scraper across configured categories.
        """

        if self.config is None:
            raise ValueError(
                "ScraperConfig is required for web extraction."
            )

        if self.fetcher is None:
            raise ValueError(
                "Fetcher is required for web extraction."
            )

        for category_path in self.config.category_paths:

            print(
                f"\nStarting category: {category_path}"
            )

            self.scrape_category(category_path)

    # BROCHURE / OCR SCRAPER
    def run_brochure_extractor(self):
        """
        Runs a brochure/OCR/API scraper.

        The scraper handles its own source and extraction logic.
        """

        products = self.extractor.extract_products()

        self.add_products(products)

        print(
            f"\nExtractor returned {len(products)} products."
        )

    # MAIN ENGINE
    def run(self):
        """
        Runs the selected retailer scraper.

        The engine does not know which retailer it is running.

        It only checks whether the scraper requires
        the generic web Fetcher.
        """

        if self.extractor is None:
            raise ValueError(
                "No extractor/plugin was provided."
            )

        print(
            f"\nStarting scraper: "
            f"{self.extractor.__class__.__name__}"
        )

        # Web-based scraper.
        if self.extractor.requires_fetcher:

            self.run_web_extractor()

        # Brochure/OCR-based scraper.
        else:

            self.run_brochure_extractor()

        print(
            f"\nEngine collected "
            f"{len(self.products)} unique products."
        )

        return self.products