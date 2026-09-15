# Main entry point for the PikSou scraping engine.


from engine.fetcher import Fetcher
from engine.scraper import ScraperEngine
from config.scraper_config import ScraperConfig
from exporters.csv_exporter import CSVExporter


def main():

    # Configure the scraper.
    config = ScraperConfig(
        base_url="https://www.winners.mu",
        page_url_template="?pagenumber={page}",
        start_page=1,
        max_pages=100
    )

    # Create the HTTP fetcher.
    fetcher = Fetcher(
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=10
    )

    # Create the main scraping engine.
    scraper = ScraperEngine(
        fetcher=fetcher,
        config=config
    )

    # Create the CSV exporter.
    exporter = CSVExporter()

    # The website-specific extractor will be added here.
    # We will create the Winners extractor next.

    # products = scraper.scrape_pages(extractor)

    # exporter.export(products, "winners_products.csv")


if __name__ == "__main__":
    main()