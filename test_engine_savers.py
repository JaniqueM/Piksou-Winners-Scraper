from engine.scraper import ScraperEngine
from extractors.savers_extractor import SaversExtractor
from exporters.csv_exporter import CSVExporter


# ---------------------------------------------------------
# SAVERS PLUGIN
# ---------------------------------------------------------

extractor = SaversExtractor()


# ---------------------------------------------------------
# ENGINE
# ---------------------------------------------------------

engine = ScraperEngine(
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
    "data/savers_products_engine.csv"
)