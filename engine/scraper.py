#Core scraping engine responsible for running
#independent retailer extractors and collecting products.

class ScraperEngine:

    def __init__(self, fetcher=None, config=None, extractor=None):

        #Optional reusable HTTP fetcher.
        self.fetcher = fetcher

        #Optional configuration for website scraping.
        self.config = config

        #The plugin/extractor being used.
        self.extractor = extractor

        #Stores all collected products.
        self.products = []

        #Keeps record of products already collected.
        self.seen_product_ids = set()

    def fetch_page(self, url):
        """
        Fetch a webpage using the configured Fetcher.
        """

        if self.fetcher is None:
            raise ValueError(
                "A Fetcher is required for web-based extractors."
            )

        return self.fetcher.get(url)

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

    def add_products(self, products):
        """
        Adds products while preventing duplicates.

        Products with a product_id use that ID.

        Products without a product_id use a combination
        of name, price, old price, and source.
        """

        for product in products:

            #Use product ID when available.
            if product.product_id is not None:

                unique_key = (
                    "id",
                    product.product_id
                )

            else:

                #Brochure/OCR products may not have product IDs.
                unique_key = (
                    "product",
                    product.source,
                    product.name,
                    product.price,
                    product.old_price
                )

            #Skip duplicates.
            if unique_key in self.seen_product_ids:
                continue

            #Record product.
            self.seen_product_ids.add(unique_key)

            #Store product.
            self.products.append(product)

    def scrape_category(self, category_path):
        """
        Scrapes all pages within one website category.

        This is only used by web-based extractors.
        """

        if self.config is None:
            raise ValueError(
                "ScraperConfig is required for category scraping."
            )

        page = self.config.start_page

        while page <= self.config.max_pages:

            #Builds URL.
            page_url = self.build_page_url(
                category_path,
                page
            )

            #Fetches page.
            response = self.fetch_page(page_url)

            #Stops if request failed.
            if response is None:
                break

            #Extract products using the selected plugin.
            products = self.extractor.extract_products(response)

            #Stop when no products are found.
            if not products:
                break

            #Add products.
            self.add_products(products)

            print(
                f"Fetched category {category_path} "
                f"page {page}: {len(products)} products"
            )

            page += 1

    def run_web_extractor(self):
        """
        Runs a web-based extractor across configured categories.
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

    def run_brochure_extractor(self):
        """
        Runs a brochure/OCR/API extractor.

        The plugin handles its own source and extraction logic.
        """

        products = self.extractor.extract_products()

        self.add_products(products)

        print(
            f"\nExtractor returned {len(products)} products."
        )

    def run(self):
        """
        Runs the selected extractor.

        The engine does not know which retailer the plugin belongs to.
        It only knows whether the plugin requires the generic Fetcher.
        """

        if self.extractor is None:
            raise ValueError(
                "No extractor/plugin was provided."
            )

        if self.extractor.requires_fetcher:

            self.run_web_extractor()

        else:

            self.run_brochure_extractor()

        print(
            f"\nEngine collected {len(self.products)} unique products."
        )

        return self.products