#Testing to check if the product.py script works for extracting the data needed
from models.product import Product

product = Product(
    product_id="8634",
    name="DANESITA BUTTER COOKIES 454G",
    sku="100085",
    price="Rs129.95",
    url="https://www.winners.mu/",
    category="biscuiterie-sucree"
)

print("Product ID:", product.product_id)
print("Name:", product.name)
print("SKU:", product.sku)
print("Price:", product.price)
print("URL:", product.url)
print("Category:", product.category)