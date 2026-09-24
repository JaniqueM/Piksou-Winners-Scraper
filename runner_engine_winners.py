from engine.scraper import ScraperEngine

from engine.fetcher import Fetcher

from config.scraper_config import ScraperConfig

from scrapers_plugins.winners_scraper import WinnersExtractor

from exporters.csv_exporter import CSVExporter


# ---------------------------------------------------------
# WINNERS CONFIGURATION
# ---------------------------------------------------------

config = ScraperConfig(

    base_url="https://www.winners.mu",

    category_paths=[
        "/epicerie",
        "/cremerie",
        "/bricomaisonjardin"
    ],

    page_url_template="?pagenumber={page}",

    start_page=1,

    max_pages=5
)


# ---------------------------------------------------------
# FETCHER
# ---------------------------------------------------------

fetcher = Fetcher(

    headers={
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/153.0.0.0 "
            "Safari/537.36"
        )
    },

    timeout=30
)


# ---------------------------------------------------------
# WINNERS PLUGIN
# ---------------------------------------------------------

extractor = WinnersExtractor()


# ---------------------------------------------------------
# ENGINE
# ---------------------------------------------------------

engine = ScraperEngine(

    fetcher=fetcher,

    config=config,

    extractor=extractor
)


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

products = engine.run()


# ---------------------------------------------------------
# EXPORT
# ---------------------------------------------------------

exporter = CSVExporter()

exporter.export(
    products,
    "data/winners_products.csv"
)