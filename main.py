# Main entry point for the PikSou scraping engine.


from engine.fetcher import Fetcher
from engine.scraper import ScraperEngine
from config.scraper_config import ScraperConfig
from exporters.csv_exporter import CSVExporter
from extractors.winners_extractor import WinnersExtractor


def main():

    category_paths = [
        "/interior-car",
        "/boucherie",
        "/boulangerie",
        "/bricomaisonjardin",
        "/cremerie",
        "/epicerie",
        "/jouets-loisirs",
        "/librairiepapeteriebagage",
        "/liquide",
        "/menage",
        "/micro-bureautique",
        "/patisserie",
        "/poissonnerie",
        "/porc",
        "/surgeles",
        "/tabac",
        "/textile",
        "/tvvideohifison",
        "/ultra-frais",
        "/volailles"
    ]

    config = ScraperConfig(
        base_url="https://www.winners.mu",
        category_paths=category_paths,
        page_url_template="?pagenumber={page}",
        start_page=1,
        max_pages=5
    )

    fetcher = Fetcher(
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=10
    )

    scraper = ScraperEngine(
        fetcher=fetcher,
        config=config
    )

    extractor = WinnersExtractor()

    exporter = CSVExporter()

    products = scraper.scrape(extractor)

    exporter.export(
        products,
        "winners_products.csv"
    )


if __name__ == "__main__":
    main()