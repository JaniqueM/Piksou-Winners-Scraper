#Exports standardized Product objects to CSV files.
import csv

class CSVExporter:

    def export(self, products, filename):

        fieldnames = [
            "product_id",
            "name",
            "sku",
            "price",
            "old_price",
            "discount_percent",
            "promotion",
            "url",
            "category",
            "source",
            "page",
            "promo_start",
            "promo_end"
        ]

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            #Writes CSV header.
            writer.writeheader()

            #Writes products.
            for product in products:

                writer.writerow({
                    "product_id": product.product_id,
                    "name": product.name,
                    "sku": product.sku,
                    "price": product.price,
                    "old_price": product.old_price,
                    "discount_percent": product.discount_percent,
                    "promotion": product.promotion,
                    "url": product.url,
                    "category": product.category,
                    "source": product.source,
                    "page": product.page,
                    "promo_start": product.promo_start,
                    "promo_end": product.promo_end
                })

        print(
            f"Exported {len(products)} products "
            f"to {filename}"
        )