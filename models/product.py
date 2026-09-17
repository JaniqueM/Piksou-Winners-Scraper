# Provides product details that we want the scraper to extract
# - will apply to any website or brochure being scraped
class Product:
    def __init__(
        self,
        product_id=None,
        name=None,
        sku=None,
        price=None,
        old_price=None,
        promotion=None,
        url=None,
        category=None,
        source=None,
        promo_start=None,
        promo_end=None
    ):
        self.product_id = product_id
        self.name = name
        self.sku = sku
        self.price = price
        self.old_price = old_price
        self.promotion = promotion
        self.url = url
        self.category = category
        self.source = source
        self.promo_start = promo_start
        self.promo_end = promo_end