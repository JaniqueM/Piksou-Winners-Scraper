# Savers brochure/OCR scraper.
#
# This is an independent PikSou plugin.
#
# The generic engine does NOT handle:
# 1. Savers PDF
# 2. OCR
# 3. Tesseract
# 4. price detection
# 5. product detection
#
# The plugin returns standardized Product objects
# to the generic ScraperEngine.


import re
from pathlib import Path

import pymupdf
import pytesseract

from PIL import Image

from scrapers_plugins.base_scraper import BaseScraper
from models.product import Product


class SaversExtractor(BaseScraper):

    # Savers manages its own PDF and OCR.
    requires_fetcher = False

    # ---------------------------------------------------------
    # CONFIGURATION
    # ---------------------------------------------------------

    PDF_FILE = Path(
        "data/savers_brochure.pdf"
    )

    TESSERACT_PATH = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    # Minimum OCR confidence.
    MIN_CONFIDENCE = 45

    # Maximum distance between current and old prices.
    MAX_X_DISTANCE = 300
    MAX_Y_DISTANCE = 110

    # Discount limits.
    MIN_DISCOUNT = 5
    MAX_DISCOUNT = 90

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(self):

        # Tell pytesseract where Tesseract is installed.
        pytesseract.pytesseract.tesseract_cmd = (
            self.TESSERACT_PATH
        )

    # ---------------------------------------------------------
    # PRICE PARSING
    # ---------------------------------------------------------

    def parse_price(self, text):

        if text is None:
            return None

        text = str(text).strip()

        text = (
            text
            .replace("Rs", "")
            .replace("rs", "")
            .replace("R$", "")
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        match = re.search(
            r"\d+(?:\.\d{1,2})?",
            text
        )

        if not match:
            return None

        try:
            return float(
                match.group(0)
            )

        except ValueError:
            return None

    # ---------------------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------------------

    def clean_text(self, text):

        if not text:
            return ""

        text = str(text)

        text = text.replace(
            "\n",
            " "
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # ---------------------------------------------------------
    # OCR WORD EXTRACTION
    # ---------------------------------------------------------

    def extract_words(self, image):

        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT
        )

        words = []

        total = len(
            data["text"]
        )

        for i in range(total):

            text = data["text"][i].strip()

            if not text:
                continue

            try:

                confidence = float(
                    data["conf"][i]
                )

            except (
                ValueError,
                TypeError
            ):

                continue

            if confidence < self.MIN_CONFIDENCE:
                continue

            words.append({

                "text": text,

                "x": int(
                    data["left"][i]
                ),

                "y": int(
                    data["top"][i]
                ),

                "width": int(
                    data["width"][i]
                ),

                "height": int(
                    data["height"][i]
                ),

                "confidence": confidence
            })

        return words

    # ---------------------------------------------------------
    # FIND PRICE CANDIDATES
    # ---------------------------------------------------------

    def find_prices(self, words):

        prices = []

        for word in words:

            value = self.parse_price(
                word["text"]
            )

            if value is None:
                continue

            if value <= 0:
                continue

            if value > 100000:
                continue

            prices.append({

                "value": value,

                "x": word["x"],

                "y": word["y"],

                "width": word["width"],

                "height": word["height"]
            })

        return prices

    # ---------------------------------------------------------
    # FIND PRICE PAIRS
    # ---------------------------------------------------------

    def find_price_pairs(self, prices):

        pairs = []

        for current in prices:

            for old in prices:

                # Same price candidate.
                if current is old:
                    continue

                # Old price must be greater.
                if old["value"] <= current["value"]:
                    continue

                x_distance = abs(
                    old["x"] - current["x"]
                )

                y_distance = abs(
                    old["y"] - current["y"]
                )

                if (
                    x_distance <= self.MAX_X_DISTANCE
                    and
                    y_distance <= self.MAX_Y_DISTANCE
                ):

                    discount = (
                        (
                            old["value"]
                            - current["value"]
                        )
                        / old["value"]
                    ) * 100

                    if discount < self.MIN_DISCOUNT:
                        continue

                    if discount > self.MAX_DISCOUNT:
                        continue

                    pairs.append({

                        "current": current,

                        "old": old,

                        "discount": round(
                            discount,
                            2
                        )
                    })

        # Remove duplicate price pairs.
        unique = []

        seen = set()

        for pair in pairs:

            key = (

                pair["current"]["value"],

                pair["current"]["x"],

                pair["current"]["y"],

                pair["old"]["value"],

                pair["old"]["x"],

                pair["old"]["y"]
            )

            if key in seen:
                continue

            seen.add(key)

            unique.append(
                pair
            )

        return unique

    # ---------------------------------------------------------
    # GET PRODUCT TEXT
    # ---------------------------------------------------------

    def get_product_text(
        self,
        words,
        price_pair
    ):

        current = price_pair[
            "current"
        ]

        old = price_pair[
            "old"
        ]

        min_x = min(
            current["x"],
            old["x"]
        ) - 500

        max_x = max(
            current["x"],
            old["x"]
        ) + 500

        min_y = min(
            current["y"],
            old["y"]
        ) - 180

        max_y = max(
            current["y"],
            old["y"]
        ) + 80

        nearby_words = []

        for word in words:

            x = word["x"]
            y = word["y"]

            if x < min_x:
                continue

            if x > max_x:
                continue

            if y < min_y:
                continue

            if y > max_y:
                continue

            # Ignore current price.
            if (
                abs(
                    x - current["x"]
                ) < 20

                and

                abs(
                    y - current["y"]
                ) < 30
            ):

                continue

            # Ignore old price.
            if (
                abs(
                    x - old["x"]
                ) < 20

                and

                abs(
                    y - old["y"]
                ) < 30
            ):

                continue

            nearby_words.append(
                word
            )

        # Reading order.
        nearby_words.sort(
            key=lambda word: (
                word["y"],
                word["x"]
            )
        )

        text = " ".join(
            word["text"]
            for word in nearby_words
        )

        return self.clean_text(
            text
        )

    # ---------------------------------------------------------
    # DETECT PROMOTION
    # ---------------------------------------------------------

    def detect_promotion(
        self,
        product_text
    ):

        text = product_text.upper()

        if "VAT ZERO" in text:
            return "VAT Zero"

        if "VAT INCL" in text:
            return "VAT Incl"

        return "Promotion"

    # ---------------------------------------------------------
    # CLEAN PRODUCT NAME
    # ---------------------------------------------------------

    def clean_product_name(
        self,
        product_text
    ):

        text = self.clean_text(
            product_text
        )

        patterns = [
            r"VAT ZERO",
            r"VAT INCL",
            r"VAT INCLUDED",
            r"PROMOTION",
            r"PROMO"
        ]

        for pattern in patterns:

            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip(
            " -:|"
        )

    # ---------------------------------------------------------
    # VALIDATE PRODUCT NAME
    # ---------------------------------------------------------

    def valid_product_name(
        self,
        name
    ):

        if not name:
            return False

        name = name.strip()

        if len(name) < 3:
            return False

        # Reject names consisting only of numbers.
        if re.fullmatch(
            r"[\d\s.,]+",
            name
        ):
            return False

        return True

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
                product.old_price,
                product.page
            )

            if key not in unique:
                unique[key] = product

        return list(
            unique.values()
        )

    # ---------------------------------------------------------
    # PROCESS ONE PAGE
    # ---------------------------------------------------------

    def process_page(
        self,
        document,
        page_number
    ):

        print(
            f"\nProcessing page "
            f"{page_number}..."
        )

        page = document[
            page_number - 1
        ]

        # Render PDF page as an image.
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(
                2,
                2
            )
        )

        image = Image.frombytes(
            "RGB",
            (
                pixmap.width,
                pixmap.height
            ),
            pixmap.samples
        )

        # Run OCR.
        words = self.extract_words(
            image
        )

        if not words:

            print(
                "No OCR words found."
            )

            return []

        # Find prices.
        prices = self.find_prices(
            words
        )

        if not prices:

            print(
                "No price candidates found."
            )

            return []

        # Find current/old price pairs.
        pairs = self.find_price_pairs(
            prices
        )

        print(
            f"Found {len(pairs)} "
            f"candidates"
        )

        products = []

        for pair in pairs:

            product_text = (
                self.get_product_text(
                    words,
                    pair
                )
            )

            product_name = (
                self.clean_product_name(
                    product_text
                )
            )

            if not self.valid_product_name(
                product_name
            ):

                continue

            promotion = (
                self.detect_promotion(
                    product_text
                )
            )

            product = Product(

                product_id=None,

                name=product_name,

                sku=None,

                price=pair[
                    "current"
                ]["value"],

                old_price=pair[
                    "old"
                ]["value"],

                discount_percent=pair[
                    "discount"
                ],

                promotion=promotion,

                url=None,

                category=None,

                source="Savers Brochure",

                page=page_number
            )

            products.append(
                product
            )

        return products

    # ---------------------------------------------------------
    # MAIN PLUGIN METHOD
    # ---------------------------------------------------------

    def extract_products(
        self,
        response=None
    ):

        # Make sure PDF exists.
        if not self.PDF_FILE.exists():

            raise FileNotFoundError(
                f"Savers brochure not found: "
                f"{self.PDF_FILE}"
            )

        # Make sure Tesseract exists.
        if not Path(
            self.TESSERACT_PATH
        ).exists():

            raise FileNotFoundError(
                f"Tesseract not found at: "
                f"{self.TESSERACT_PATH}"
            )

        print(
            "\nOpening Savers brochure..."
        )

        document = pymupdf.open(
            self.PDF_FILE
        )

        total_pages = len(
            document
        )

        print(
            f"Total pages: "
            f"{total_pages}"
        )

        all_products = []

        # Process every page.
        for page_number in range(
            1,
            total_pages + 1
        ):

            page_products = (
                self.process_page(
                    document,
                    page_number
                )
            )

            all_products.extend(
                page_products
            )

        document.close()

        # Remove duplicates.
        all_products = (
            self.remove_duplicates(
                all_products
            )
        )

        print(
            "\nSavers extraction complete."
        )

        print(
            f"Unique products: "
            f"{len(all_products)}"
        )

        return all_products