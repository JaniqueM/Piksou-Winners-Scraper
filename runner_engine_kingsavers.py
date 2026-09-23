from engine.scraper import ScraperEngine
from scrapers_plugins.kingsavers_scraper import KingSaversExtractor
from exporters.csv_exporter import CSVExporter

#KING SAVERS PLUGIN
extractor = KingSaversExtractor()

# ENGINE
engine = ScraperEngine(
    extractor=extractor
)

#RUN
products = engine.run()

#EXPORT
exporter = CSVExporter()

exporter.export(
    products,
    "data/kingsavers_products.csv"
)