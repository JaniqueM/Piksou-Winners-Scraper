from engine.scraper import ScraperEngine
from scrapers_plugins.savers_scraper import SaversExtractor
from exporters.csv_exporter import CSVExporter


extractor = SaversExtractor()

engine = ScraperEngine(
    extractor=extractor
)

products = engine.run()

exporter = CSVExporter()

exporter.export(
    products,
    "data/savers_products_engine.csv"
)