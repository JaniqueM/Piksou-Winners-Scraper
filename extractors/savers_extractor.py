import pymupdf
import pytesseract
from pytesseract import Output
from PIL import Image
import io
import re
import csv
import os


# ============================================================
# CONFIGURATION
# ============================================================

PDF_FILE = "data/savers_brochure.pdf"
OUTPUT_FILE = "data/savers_products.csv"

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================
# PRICE PARSING
# ============================================================

def parse_price(text):

    text = text.strip()
    text = text.replace(",", ".")

    # Decimal prices
    if re.fullmatch(r"\d{1,3}\.\d{1,2}", text):

        try:
            value = float(text)

            if 5 <= value <= 5000:
                return value

        except ValueError:
            return None

    # Whole-number prices
    if re.fullmatch(r"\d{1,3}", text):

        try:
            value = float(text)

            # Reject tiny OCR fragments such as 1, 2, 3, 4
            if 5 <= value <= 5000:
                return value

        except ValueError:
            return None

    return None


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    text = text.strip()

    if not text:
        return ""

    # Remove OCR vertical bars
    text = re.sub(r"[|]+", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# OCR PAGE
# ============================================================

def extract_words(page):

    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2)
    )

    image = Image.open(
        io.BytesIO(
            pixmap.tobytes("png")
        )
    )

    data = pytesseract.image_to_data(
        image,
        output_type=Output.DICT,
        config="--psm 11"
    )

    words = []

    for i, text in enumerate(data["text"]):

        text = clean_text(text)

        if not text:
            continue

        try:
            confidence = float(data["conf"][i])
        except (ValueError, TypeError):
            confidence = 0

        words.append({
            "text": text,
            "x": int(data["left"][i]),
            "y": int(data["top"][i]),
            "width": int(data["width"][i]),
            "height": int(data["height"][i]),
            "confidence": confidence
        })

    return words


# ============================================================
# FIND PRICES
# ============================================================

def find_prices(words):

    prices = []

    for word in words:

        value = parse_price(
            word["text"]
        )

        if value is None:
            continue

        # Ignore very low-confidence OCR
        if word["confidence"] < 45:
            continue

        prices.append({
            **word,
            "price": value
        })

    return prices


# ============================================================
# FIND PRICE PAIRS
# ============================================================

def find_price_pairs(prices):

    possible_pairs = []

    for i in range(len(prices)):

        for j in range(i + 1, len(prices)):

            p1 = prices[i]
            p2 = prices[j]

            value1 = p1["price"]
            value2 = p2["price"]

            if value1 == value2:
                continue

            high = max(
                value1,
                value2
            )

            low = min(
                value1,
                value2
            )

            # Reject very small OCR fragments
            if low < 5:
                continue

            # ------------------------------------------------
            # POSITION
            # ------------------------------------------------

            x_distance = abs(
                p1["x"] - p2["x"]
            )

            y_distance = abs(
                p1["y"] - p2["y"]
            )

            # Prices belonging to one product
            # should be reasonably close.
            if x_distance > 300:
                continue

            if y_distance > 110:
                continue

            # ------------------------------------------------
            # DISCOUNT
            # ------------------------------------------------

            discount = (
                (high - low)
                / high
            ) * 100

            # Ignore tiny differences
            if discount < 5:
                continue

            # Reject suspicious OCR relationships
            if discount > 90:
                continue

            # ------------------------------------------------
            # SCORE
            # ------------------------------------------------

            score = (
                x_distance * 0.4
                + y_distance * 0.6
            )

            possible_pairs.append({
                "current_price": low,
                "old_price": high,
                "discount_percent": round(
                    discount,
                    2
                ),
                "score": score,
                "price1": p1,
                "price2": p2
            })

    # Closest price pairs first
    possible_pairs.sort(
        key=lambda pair: pair["score"]
    )

    # --------------------------------------------------------
    # PREVENT REUSING THE SAME PRICE
    # --------------------------------------------------------

    used_prices = set()
    final_pairs = []

    for pair in possible_pairs:

        p1_id = id(
            pair["price1"]
        )

        p2_id = id(
            pair["price2"]
        )

        if p1_id in used_prices:
            continue

        if p2_id in used_prices:
            continue

        used_prices.add(p1_id)
        used_prices.add(p2_id)

        final_pairs.append(pair)

    return final_pairs


# ============================================================
# FIND PRODUCT TEXT
# ============================================================

def get_product_text(words, pair):

    p1 = pair["price1"]
    p2 = pair["price2"]

    left = min(
        p1["x"],
        p2["x"]
    )

    right = max(
        p1["x"] + p1["width"],
        p2["x"] + p2["width"]
    )

    top = min(
        p1["y"],
        p2["y"]
    )

    # Search around the price area.
    #
    # Product names are normally above or close to
    # the promotional price.
    search_left = left - 180
    search_right = right + 180
    search_top = max(
        0,
        top - 180
    )
    search_bottom = top + 40

    candidates = []

    for word in words:

        if word is p1 or word is p2:
            continue

        x = word["x"]
        y = word["y"]

        if x < search_left:
            continue

        if x > search_right:
            continue

        if y < search_top:
            continue

        if y > search_bottom:
            continue

        text = word["text"]

        if not text:
            continue

        upper = text.upper()

        # Ignore obvious brochure headers
        if upper in [
            "SAVERS",
            "SUPERMARKET",
            "PROMOTION",
            "PROMOTIONS",
            "BEL-AIR"
        ]:
            continue

        candidates.append(word)

    # Reading order
    candidates.sort(
        key=lambda word: (
            word["y"],
            word["x"]
        )
    )

    parts = []

    for word in candidates:

        text = word["text"]

        # Ignore standalone numbers
        if re.fullmatch(
            r"\d+([.,]\d+)?",
            text
        ):
            continue

        parts.append(text)

    product_text = " ".join(parts)

    return clean_text(
        product_text
    )


# ============================================================
# PROMOTION DETECTION
# ============================================================

def detect_promotion(text):

    upper = text.upper()

    if "VAT ZERO" in upper:
        return "VAT ZERO"

    if "VAT INCL" in upper:
        return "VAT INCL"

    return "Promotion"


# ============================================================
# PRODUCT NAME CLEANING
# ============================================================

def clean_product_name(text):

    # Remove VAT labels
    text = re.sub(
        r"\bVAT\s+ZERO\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bVAT\s+INCL\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove obvious OCR separators
    text = re.sub(
        r"[|_=~]+",
        " ",
        text
    )

    # Remove repeated spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip(
        " -|_=~"
    )


# ============================================================
# VALIDATE PRODUCT NAME
# ============================================================

def valid_product_name(name):

    if not name:
        return False

    name = name.strip()

    # Too short
    if len(name) < 8:
        return False

    # Count letters
    letters = sum(
        c.isalpha()
        for c in name
    )

    # Count digits
    digits = sum(
        c.isdigit()
        for c in name
    )

    # Count symbols
    symbols = sum(
        not c.isalnum()
        and not c.isspace()
        for c in name
    )

    # Must contain enough readable letters
    if letters < 5:
        return False

    # Reject text dominated by symbols
    if symbols > letters:
        return False

    # Reject text with very little alphabetic content
    if letters / max(len(name), 1) < 0.30:
        return False

    upper = name.upper()

    # --------------------------------------------------------
    # BROCHURE / HEADER NOISE
    # --------------------------------------------------------

    bad_phrases = [
        "OPENING HOURS",
        "SUPERMARKET SAVERS",
        "HELLO@SAVERS",
        "PROMOTION FROM",
        "ONLY @ BEL-AIR",
        "BEL-AIR OPENING",
        "SUN & P.HOLIDAY"
    ]

    for phrase in bad_phrases:

        if phrase in upper:
            return False

    # --------------------------------------------------------
    # REPEATED SYMBOL GARBAGE
    # --------------------------------------------------------

    if name.count("*") >= 3:
        return False

    if name.count("=") >= 2:
        return False

    if name.count("|") >= 2:
        return False

    # --------------------------------------------------------
    # OCR GARBAGE PATTERNS
    # --------------------------------------------------------

    garbage_patterns = [
        r"^[^A-Za-z]{0,5}$",
        r"^[*#=|~_\- ]+$",
        r"^\W+\s*[A-Za-z]{1,4}$"
    ]

    for pattern in garbage_patterns:

        if re.fullmatch(
            pattern,
            name
        ):
            return False

    return True


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(products):

    final_products = []

    seen = set()

    for product in products:

        name = (
            product["product_name"]
            .lower()
            .strip()
        )

        key = (
            product["page"],
            round(
                product["current_price"],
                2
            ),
            round(
                product["old_price"],
                2
            ),
            name
        )

        if key in seen:
            continue

        seen.add(key)

        final_products.append(
            product
        )

    return final_products


# ============================================================
# PROCESS PAGE
# ============================================================

def process_page(page, page_number):

    print(
        f"Processing page {page_number}..."
    )

    words = extract_words(page)

    prices = find_prices(words)

    print(
        f"  OCR words: {len(words)}"
    )

    print(
        f"  Prices found: {len(prices)}"
    )

    pairs = find_price_pairs(
        prices
    )

    print(
        f"  Valid price pairs: {len(pairs)}"
    )

    products = []

    for pair in pairs:

        raw_name = get_product_text(
            words,
            pair
        )

        product_name = clean_product_name(
            raw_name
        )

        # Reject bad OCR names
        if not valid_product_name(
            product_name
        ):
            continue

        promotion = detect_promotion(
            raw_name
        )

        products.append({
            "retailer": "Savers",
            "product_name": product_name,
            "current_price": pair[
                "current_price"
            ],
            "old_price": pair[
                "old_price"
            ],
            "discount_percent": pair[
                "discount_percent"
            ],
            "promotion": promotion,
            "page": page_number
        })

    return products


# ============================================================
# MAIN SCRAPER
# ============================================================

def scrape_savers():

    print("=" * 70)
    print("SAVERS PROMOTION SCRAPER")
    print("=" * 70)

    # --------------------------------------------------------
    # CHECK PDF
    # --------------------------------------------------------

    if not os.path.exists(
        PDF_FILE
    ):

        print(
            f"ERROR: PDF not found: {PDF_FILE}"
        )

        return

    # --------------------------------------------------------
    # CHECK TESSERACT
    # --------------------------------------------------------

    if not os.path.exists(
        TESSERACT_PATH
    ):

        print(
            "ERROR: Tesseract not found:"
        )

        print(
            TESSERACT_PATH
        )

        return

    # --------------------------------------------------------
    # OPEN PDF
    # --------------------------------------------------------

    print()
    print(
        "Opening Savers brochure..."
    )

    document = pymupdf.open(
        PDF_FILE
    )

    print(
        f"Total pages: {len(document)}"
    )

    all_products = []

    # --------------------------------------------------------
    # PROCESS PAGES
    # --------------------------------------------------------

    for page_index in range(
        len(document)
    ):

        page_number = (
            page_index + 1
        )

        products = process_page(
            document[page_index],
            page_number
        )

        print(
            f"  Products extracted: "
            f"{len(products)}"
        )

        all_products.extend(
            products
        )

    document.close()

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    all_products = remove_duplicates(
        all_products
    )

    # --------------------------------------------------------
    # SAVE CSV
    # --------------------------------------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "retailer",
            "product_name",
            "current_price",
            "old_price",
            "discount_percent",
            "promotion",
            "page"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            all_products
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("SAVERS SCRAPER COMPLETE")
    print("=" * 70)

    print(
        f"Total products extracted: "
        f"{len(all_products)}"
    )

    print(
        f"Output file: {OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    scrape_savers()