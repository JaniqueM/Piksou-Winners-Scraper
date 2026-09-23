#Provides standardized product details for all PikSou extractors.
#The same Product model is used for:
#1. Websites
#2. PDFs
#3. OCR brochures
#4. Future APIs
#5. Other retailer plugins


class Product:

    def __init__(
        self,
        product_id=None,
        name=None,
        sku=None,
        price=None,
        old_price=None,
        discount_percent=None,
        promotion=None,
        url=None,
        category=None,
        source=None,
        page=None,
        promo_start=None,
        promo_end=None
    ):

        #Retailer product ID.
        self.product_id = product_id

        #Product name.
        self.name = name

        #Stock keeping unit.
        self.sku = sku

        #Current selling price.
        self.price = price

        #Previous/original price.
        self.old_price = old_price

        #Calculated percentage discount.
        self.discount_percent = discount_percent

        #Promotion information.
        self.promotion = promotion

        #Product URL.
        self.url = url

        #Website category.
        self.category = category

        #Source of the product.
        self.source = source

        #Brochure page.
        self.page = page

        #Promotion starting date.
        self.promo_start = promo_start

        #Promotion ending date.
        self.promo_end = promo_end