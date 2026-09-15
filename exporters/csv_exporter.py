# Exports standardized product data to CSV files.

import csv

class CSVExporter:

    def export(self, products, filename):
        # Defines the columns that will be written to the CSV file.
        fieldnames = [
            "product_id",
            "name",
            "sku",
            "price",
            "url",
            "category"
        ]

        # Opens the CSV file for writing.
        with open(filename, "w", newline="", encoding="utf-8") as file:

            # Creates a CSV writer using the defined column names.
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            # Writes the column headers.
            writer.writeheader()

            # Writes each Product object as a row.
            for product in products:

                writer.writerow({
                    "product_id": product.product_id,
                    "name": product.name,
                    "sku": product.sku,
                    "price": product.price,
                    "url": product.url,
                    "category": product.category
                })

        print(f"Exported {len(products)} products to {filename}")