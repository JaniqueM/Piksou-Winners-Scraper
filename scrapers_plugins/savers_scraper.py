import os
import re

import requests
import pymupdf
import pytesseract

from PIL import Image
from bs4 import BeautifulSoup
from pytesseract import Output

from scrapers_plugins.base_scraper import BaseScraper
from models.product import Product


class SaversExtractor(BaseScraper):

    requires_fetcher = False

    WEBSITE_URL = "https://savers.mu/"
    BROCHURE_URL = "https://savers.mu/brochure/"
    ARCHIVE_URL = "https://savers.mu/archive/"

    PDF_PATH = os.path.join(
        "data",
        "savers_brochure.pdf"
    )

    TESSERACT_PATH = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    MIN_CONFIDENCE = 50

    # The Savers brochure has approximately four
    # product columns across the page.
    COLUMN_RANGES = [
        (0, 312),
        (312, 624),
        (624, 936),
        (936, 1248)
    ]

    def __init__(self):

        os.makedirs(
            "data",
            exist_ok=True
        )

        pytesseract.pytesseract.tesseract_cmd = (
            self.TESSERACT_PATH
        )

    # DOWNLOAD BROCHURE
    def download_brochure(self):

        print("\nChecking Savers website for brochure...")

        pages = [
            self.BROCHURE_URL,
            self.WEBSITE_URL,
            self.ARCHIVE_URL
        ]

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/153.0.0.0 "
                "Safari/537.36"
            )
        }

        pdf_links = []

        for page_url in pages:

            try:

                response = requests.get(
                    page_url,
                    headers=headers,
                    timeout=30
                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                for link in soup.find_all(
                    "a",
                    href=True
                ):

                    href = link["href"]

                    if ".pdf" not in href.lower():
                        continue

                    if href.startswith("//"):

                        href = "https:" + href

                    elif href.startswith("/"):

                        href = (
                            "https://savers.mu"
                            + href
                        )

                    elif not href.startswith("http"):

                        continue

                    pdf_links.append(href)

            except Exception as error:

                print(
                    f"Could not check {page_url}: "
                    f"{error}"
                )

        if not pdf_links:

            raise RuntimeError(
                "No Savers PDF brochure was found."
            )

        pdf_links = list(
            dict.fromkeys(pdf_links)
        )

        preferred = []

        for url in pdf_links:

            lower_url = url.lower()

            if any(
                word in lower_url
                for word in [
                    "brochure",
                    "promo",
                    "promotion",
                    "catalogue",
                    "catalog"
                ]
            ):

                preferred.append(url)

        if preferred:

            brochure_url = preferred[0]

        else:

            brochure_url = pdf_links[0]

        print(
            f"Downloading brochure:\n"
            f"{brochure_url}"
        )

        response = requests.get(
            brochure_url,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()

        with open(
            self.PDF_PATH,
            "wb"
        ) as file:

            file.write(response.content)

        print(
            f"Brochure saved to: "
            f"{self.PDF_PATH}"
        )

    # PRICE DETECTION
    def parse_price(self, text):

        if not text:
            return None

        text = text.strip()

        cleaned = re.sub(
            r"[^\d.,]",
            "",
            text
        )

        if not cleaned:
            return None

        cleaned = cleaned.replace(
            ",",
            "."
        )

        if cleaned.count(".") > 1:

            parts = cleaned.split(".")

            cleaned = (
                parts[0]
                + "."
                + "".join(parts[1:])
            )

        try:

            value = float(cleaned)

        except ValueError:

            return None

        # Reject obvious OCR garbage.
        if value < 10:
            return None

        if value > 5000:
            return None

        return value

    def is_price(self, text):

        if not text:
            return False

        text = text.strip()

        pattern = (
            r"^\d{1,4}"
            r"(?:[.,]\d{1,2})?$"
        )

        if not re.fullmatch(
            pattern,
            text
        ):

            return False

        return (
            self.parse_price(text)
            is not None
        )

    # IGNORE BROCHURE / OCR NOISE
    def is_noise(self, text):

        if not text:
            return True

        lower = text.lower().strip()

        noise_words = [
            "vat",
            "zero",
            "incl",
            "inclusive",
            "promotion",
            "promotions",
            "opening",
            "hours",
            "hello@savers.mu",
            "savers.mu",
            "supermarket",
            "while stocks last",
            "terms",
            "conditions",

            "mon",
            "monday",
            "tue",
            "tuesday",
            "wed",
            "wednesday",
            "thu",
            "thursday",
            "fri",
            "friday",
            "sat",
            "saturday",
            "sun",
            "sunday",

            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",

            "from",
            "to"
        ]

        for noise in noise_words:

            if noise in lower:
                return True

        return False

    # CHECK PRODUCT TEXT
    def looks_like_product_text(self, text):

        if not text:
            return False

        text = text.strip()

        if self.is_noise(text):
            return False

        if self.is_price(text):
            return False

        # Product text should contain letters.
        letters = re.findall(
            r"[A-Za-zÀ-ÿ]",
            text
        )

        if len(letters) < 3:
            return False

        # Reject isolated OCR symbols.
        if text in [
            ">",
            "<",
            "/",
            "-",
            "_",
            "|",
            ":"
        ]:
            return False

        return True

    # CLEAN PRODUCT NAME
    def clean_product_name(self, words):

        words = sorted(
            words,
            key=lambda item: (
                item["y"],
                item["x"]
            )
        )

        result = []

        for word in words:

            text = word["text"].strip()

            if not text:
                continue

            if self.is_noise(text):
                continue

            if self.is_price(text):
                continue

            if not self.looks_like_product_text(text):
                continue

            result.append(text)

        # Remove immediately repeated OCR words.
        cleaned = []

        for word in result:

            if not cleaned:

                cleaned.append(word)
                continue

            if (
                word.lower()
                == cleaned[-1].lower()
            ):

                continue

            cleaned.append(word)

        name = " ".join(cleaned)

        # Remove leading OCR punctuation.
        name = re.sub(
            r"^[^\w]+",
            "",
            name
        )

        # Remove trailing OCR punctuation.
        name = re.sub(
            r"[^\w)]+$",
            "",
            name
        )

        # Remove repeated spaces.
        name = re.sub(
            r"\s+",
            " ",
            name
        )

        return name.strip()

    # OCR ONE COLUMN
    def process_column(
        self,
        image,
        x_start,
        x_end,
        page_number
    ):

        column = image.crop(
            (
                x_start,
                0,
                x_end,
                image.height
            )
        )

        data = pytesseract.image_to_data(
            column,
            config="--psm 11",
            output_type=Output.DICT
        )

        words = []

        for i in range(
            len(data["text"])
        ):

            text = data["text"][i].strip()

            if not text:
                continue

            try:

                confidence = float(
                    data["conf"][i]
                )

            except Exception:

                continue

            if confidence < self.MIN_CONFIDENCE:
                continue

            words.append({
                "text": text,
                "x": data["left"][i],
                "y": data["top"][i],
                "w": data["width"][i],
                "h": data["height"][i],
                "confidence": confidence
            })

        # FIND PRICE CANDIDATES
        prices = []

        for word in words:

            if not self.is_price(
                word["text"]
            ):

                continue

            value = self.parse_price(
                word["text"]
            )

            if value is None:
                continue

            prices.append({
                **word,
                "value": value
            })

        prices.sort(
            key=lambda item: (
                item["y"],
                item["x"]
            )
        )

        products = []

        # MATCH PRICE TO PRODUCT NAME
        for price_index, price in enumerate(prices):

            current_price = price["value"]

            price_x = price["x"]
            price_y = price["y"]

            # Find the next price below this price.
            next_price_y = None

            for other_index, other_price in enumerate(prices):

                if other_index <= price_index:
                    continue

                if other_price["y"] > price_y:

                    next_price_y = other_price["y"]
                    break

            # Find product words below the price.
            name_words = []

            for word in words:

                if word is price:
                    continue

                word_x = word["x"]
                word_y = word["y"]

                vertical_distance = (
                    word_y - price_y
                )

                # Product name must be below price.
                if vertical_distance < 15:
                    continue

                # Allow multiple lines of product names.
                if vertical_distance > 190:
                    continue

                # Stop when next price is reached.
                if (
                    next_price_y is not None
                    and word_y >= next_price_y
                ):

                    continue

                if self.is_price(
                    word["text"]
                ):

                    continue

                if not self.looks_like_product_text(
                    word["text"]
                ):

                    continue

                # Horizontal proximity.
                # Increased from 125 to 170 because some
                # legitimate product names extend beyond price position.

                word_center = (
                    word_x
                    + word["w"] / 2
                )

                price_center = (
                    price_x
                    + price["w"] / 2
                )

                horizontal_distance = abs(
                    word_center
                    - price_center
                )

                if horizontal_distance > 170:
                    continue

                name_words.append(word)

            name = self.clean_product_name(
                name_words
            )

            # Reject bad OCR.
            if not name:
                continue

            if len(name) < 4:
                continue

            letter_count = len(
                re.findall(
                    r"[A-Za-zÀ-ÿ]",
                    name
                )
            )

            if letter_count < 4:
                continue

            # Reject obvious brochure headings.
            lower_name = name.lower()

            bad_name_patterns = [
                "promotion",
                "opening hours",
                "while stocks",
                "terms conditions",
                "hello@savers",
                "from june",
                "from july",
                "from august",
                "from september",
                "from october",
                "to july",
                "to august",
                "to september",
                "to october"
            ]

            if any(
                pattern in lower_name
                for pattern in bad_name_patterns
            ):

                continue

            # Limit extremely long OCR merges.
            if len(name) > 120:

                name = name[:120].strip()

            # FIND OLD PRICE
            old_price = None

            for other_index, other_price in enumerate(prices):

                if other_index == price_index:
                    continue

                price_center = (
                    price_x
                    + price["w"] / 2
                )

                other_center = (
                    other_price["x"]
                    + other_price["w"] / 2
                )

                x_distance = abs(
                    other_center
                    - price_center
                )

                y_distance = abs(
                    other_price["y"]
                    - price_y
                )

                if x_distance > 100:
                    continue

                if y_distance > 80:
                    continue

                candidate = other_price["value"]

                if candidate <= current_price:
                    continue

                if candidate > current_price * 5:
                    continue

                old_price = candidate
                break

            # CALCULATE DISCOUNT
            discount = None
            promotion = False

            if old_price is not None:

                discount = round(
                    (
                        (
                            old_price
                            - current_price
                        )
                        / old_price
                    ) * 100,
                    2
                )

                if 0 < discount <= 90:

                    promotion = True

                else:

                    old_price = None
                    discount = None

            # CREATE PRODUCT
            product = Product(
                product_id=None,
                name=name,
                sku=None,
                price=current_price,
                old_price=old_price,
                discount_percent=discount,
                promotion=promotion,
                url=None,
                category=None,
                source="Savers Brochure",
                page=page_number
            )

            products.append(product)

        return products

    # PROCESS PAGE
    def process_page(
        self,
        page,
        page_number
    ):

        print(
            f"\nProcessing page "
            f"{page_number}..."
        )

        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(
                2,
                2
            ),
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            (
                pixmap.width,
                pixmap.height
            ),
            pixmap.samples
        )

        page_products = []

        # Our OCR coordinate measurements were based
        # on a 1248 px wide page.
        scale_x = image.width / 1248

        for x_start, x_end in self.COLUMN_RANGES:

            real_start = int(
                x_start * scale_x
            )

            real_end = int(
                x_end * scale_x
            )

            products = self.process_column(
                image,
                real_start,
                real_end,
                page_number
            )

            page_products.extend(
                products
            )

        return page_products

    # MAIN EXTRACTION
    def extract_products(
        self,
        response=None
    ):

        self.download_brochure()

        document = pymupdf.open(
            self.PDF_PATH
        )

        all_products = []

        print(
            f"\nSavers brochure contains "
            f"{len(document)} pages."
        )

        for page_number in range(
            len(document)
        ):

            page = document[
                page_number
            ]

            products = self.process_page(
                page,
                page_number + 1
            )

            print(
                f"Found "
                f"{len(products)} "
                f"possible products."
            )

            all_products.extend(
                products
            )

        document.close()

        print(
            f"\nTotal products extracted: "
            f"{len(all_products)}"
        )

        return all_products