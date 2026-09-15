#Provides product details that we want the scraper to extract - will apply to any website being scrapped 
class Product:
    def __init__(
        self,
        product_id=None,
        name=None,
        sku=None,
        price=None,
        url=None,
        category=None
    ):
        self.product_id = product_id
        self.name = name
        self.sku = sku
        self.price = price
        self.url = url
        self.category = category