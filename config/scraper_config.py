#Stores configurable settings used by the generic scraper engine.

class ScraperConfig:
    def __init__(
        self,
        base_url,
        page_parameter="pagenumber",
        start_page=1
    ):
        self.base_url = base_url
        self.page_parameter = page_parameter
        self.start_page = start_page