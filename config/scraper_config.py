# Stores configurable settings used by the generic scraper engine.


class ScraperConfig:

    def __init__(
        self,
        base_url,
        category_paths=None,
        page_url_template="?pagenumber={page}",
        start_page=1,
        max_pages=5
    ):
        # Main website URL.
        self.base_url = base_url

        # Website category paths.
        self.category_paths = category_paths or []

        # Pattern used to create page URLs.
        self.page_url_template = page_url_template

        # First page to scrape.
        self.start_page = start_page

        # Maximum number of pages to scrape per category.
        self.max_pages = max_pages