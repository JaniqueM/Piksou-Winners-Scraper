# Exports standardized product data to CSV files.

import csv


class CSVExporter:

    def export(self, products, filename):

        fieldnames = [
            "product_id",
            "name",
            "sku",
            "price",
            "old_price",
            "promotion",
            "url",
            "category",
            "source",
            "promo_start",
            "promo_end"
        ]

        with open(filename, "w", newline="", encoding="utf-8") as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for product in products:

                writer.writerow({
                    "product_id": product.product_id,
                    "name": product.name,
                    "sku": product.sku,
                    "price": product.price,
                    "old_price": product.old_price,
                    "promotion": product.promotion,
                    "url": product.url,
                    "category": product.category,
                    "source": product.source,
                    "promo_start": product.promo_start,
                    "promo_end": product.promo_end
                })

        print(f"Exported {len(products)} products to {filename}")