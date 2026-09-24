# King Savers brochure scraper.

# The generic engine does NOT know:
# 1. how the King Savers PDF works
# 2. how prices are formatted
# 3. how promotions are identifies
# This plugin handles all of that itself.

import re
from pathlib import Path

import requests
import pymupdf

from scrapers_plugins.base_scraper import BaseScraper
from models.product import Product


class KingSaversExtractor(BaseScraper):

    # King Savers handles its own PDF.
    # Therefore the generic HTTP Fetcher is not required.
    requires_fetcher = False

    # CONFIGURATION
    BROCHURE_URL = (
        "https://www.king-savers.com/"
        "wp-content/uploads/2026/07/"
        "KS-EOM-JUL-2026_LR-compressed.pdf"
    )

    DATA_DIR = Path("data")

    BROCHURE_PATH = (
        DATA_DIR / "kingsavers_brochure.pdf"
    )

    # DOWNLOAD BROCHURE
    def download_brochure(self):

        self.DATA_DIR.mkdir(
            exist_ok=True
        )

        print(
            "Downloading King Savers brochure..."
        )

        response = requests.get(
            self.BROCHURE_URL,
            timeout=60
        )

        response.raise_for_status()

        with open(
            self.BROCHURE_PATH,
            "wb"
        ) as file:

            file.write(
                response.content
            )

        print(
            f"Brochure saved to: "
            f"{self.BROCHURE_PATH}"
        )

    # READ PDF
    def extract_pages(self):

        print(
            "Opening King Savers brochure..."
        )

        document = pymupdf.open(
            self.BROCHURE_PATH
        )

        pages = []

        total_pages = len(document)

        for page_number, page in enumerate(
            document,
            start=1
        ):

            text = page.get_text(
                "text"
            )

            pages.append({
                "page": page_number,
                "text": text
            })

            print(
                f"Read page "
                f"{page_number}/{total_pages}"
            )

        document.close()

        return pages

    # PRICE DETECTION
    def is_price(self, line):

        return re.match(
            r"^Rs\s*[0-9]+(?:\.[0-9]{1,2})?$",
            line,
            re.IGNORECASE
        ) is not None

    # GET PRICE
    def get_price(self, line):

        match = re.match(
            r"^Rs\s*([0-9]+(?:\.[0-9]{1,2})?)$",
            line,
            re.IGNORECASE
        )

        if match:

            return float(
                match.group(1)
            )

        return None

    # IGNORE UNWANTED LINES
    def is_ignored_line(self, line):

        ignored_patterns = [

            r"^Vat\s+",
            r"^PROMO:",
            r"^OFFRE VALABLE",
            r"^CERTAINS PRODUITS",
            r"^PAS DISPONIBLES",
            r"^POUR NOS HORAIRES",
            r"^D['’]OUVERTURE",
            r"^VISITEZ NOTRE PAGE",
            r"^TEL:",
            r"^BEAU VALLON",
            r"^BO['’]VALON MALL",
            r"^GOODLANDS",
            r"^VIP VILLAGE",
            r"^OPP HURRY",
            r"^NEW GROVE",
            r"^LA CROISÉE",
            r"^ROYAL ROAD",
            r"^SURINAM",
            r"^BONNE TERRE",
            r"^VACOAS",
            r"^THU ",
            r"^FRI ",
            r"^SAT ",
            r"^[0-9]+$"
        ]

        for pattern in ignored_patterns:

            if re.search(
                pattern,
                line,
                re.IGNORECASE
            ):

                return True

        return False

    # CLEAN PRODUCT NAME
    def clean_product_name(self, lines):

        cleaned = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if self.is_ignored_line(line):
                continue

            cleaned.append(line)

        return " ".join(
            cleaned
        )

    # EXTRACT PROMOTIONS FROM PAGE
    def extract_promotions_from_page(
        self,
        page_number,
        text
    ):

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        promotions = []

        product_lines = []

        i = 0

        while i < len(lines):

            line = lines[i]

            # Ignore general brochure information.
            if self.is_ignored_line(line):

                i += 1
                continue

            # PRICE FOUND
            if self.is_price(line):

                current_price = self.get_price(
                    line
                )

                old_price = None

                # Check whether the next line
                # contains the old price.
                if (
                    i + 1 < len(lines)
                    and self.is_price(lines[i + 1])
                ):

                    possible_old_price = (
                        self.get_price(
                            lines[i + 1]
                        )
                    )

                    if (
                        possible_old_price
                        > current_price
                    ):

                        old_price = (
                            possible_old_price
                        )

                        i += 1

                # Build product name.
                product_name = (
                    self.clean_product_name(
                        product_lines
                    )
                )

                if product_name:

                    discount = None

                    if old_price:

                        discount = round(
                            (
                                (
                                    old_price
                                    - current_price
                                )
                                / old_price
                            )
                            * 100,
                            2
                        )

                    # Create standardized Product.
                    product = Product(

                        product_id=None,

                        name=product_name,

                        sku=None,

                        price=current_price,

                        old_price=old_price,

                        discount_percent=discount,

                        promotion=True,

                        url=None,

                        category=None,

                        source=(
                            "King Savers Brochure"
                        ),

                        page=page_number
                    )

                    promotions.append(
                        product
                    )

                # Reset product text.
                product_lines = []

                i += 1

                continue

            # Normal text belongs to
            # the current product.
            product_lines.append(
                line
            )

            i += 1

        return promotions

    # ---------------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------------

    def remove_duplicates(
        self,
        products
    ):

        unique = {}

        for product in products:

            key = (
                product.name.lower().strip(),
                product.price,
                product.old_price
            )

            if key not in unique:

                unique[key] = product

        return list(
            unique.values()
        )

    # MAIN PLUGIN METHOD
    def extract_products(
        self,
        response=None
    ):

        # Download only if the brochure
        # does not already exist.
        if not self.BROCHURE_PATH.exists():

            self.download_brochure()

        else:

            print(
                "Using existing King Savers brochure."
            )

        # Extract PDF text.
        pages = self.extract_pages()

        all_products = []

        # Process every page.
        for page in pages:

            page_products = (
                self.extract_promotions_from_page(
                    page["page"],
                    page["text"]
                )
            )

            all_products.extend(
                page_products
            )

            print(
                f"Page {page['page']}: "
                f"{len(page_products)} "
                f"promotions found"
            )

        # Remove duplicates.
        all_products = (
            self.remove_duplicates(
                all_products
            )
        )

        print(
            "\nKing Savers extraction complete."
        )

        print(
            f"Unique products: "
            f"{len(all_products)}"
        )

        return all_products