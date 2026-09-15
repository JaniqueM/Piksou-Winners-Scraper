# Stores configurable settings used by the generic scraper engine.


class ScraperConfig:
    def __init__(
        self,
        base_url,
        page_url_template="?pagenumber={page}",
        start_page=1
    ):
        self.base_url = base_url
        self.page_url_template = page_url_template
        self.start_page = start_page