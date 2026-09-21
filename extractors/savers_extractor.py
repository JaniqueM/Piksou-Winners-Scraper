import pymupdf
import pytesseract
from pytesseract import Output
from PIL import Image
import io
import re
import csv
import os

PDF_FILE = "data/savers_brochure.pdf"
OUTPUT_FILE = "data/savers_products.csv"

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ---------------------------------------------------------
# PRICE DETECTION
# ---------------------------------------------------------

def parse_price(text):
    """
    Convert OCR text into a price.

    Accepts:
        69.50
        79.90
        50
        241.5

    Rejects:
        very large numbers
        obvious non-price values
    """

    text = text.strip()
    text = text.replace(",", ".")

    # Normal decimal price
    if re.fullmatch(r"\d{1,3}\.\d{1,2}", text):
        try:
            value = float(text)

            if 1 <= value <= 10000:
                return value

        except ValueError:
            pass

    # Whole number price
    if re.fullmatch(r"\d{1,3}", text):
        try:
            value = float(text)

            if 1 <= value <= 5000:
                return value

        except ValueError:
            pass

    return None


# ---------------------------------------------------------
# CLEAN OCR TEXT
# ---------------------------------------------------------

def clean_text(text):
    text = text.strip()

    if not text:
        return ""

    # Remove obvious OCR garbage
    text = re.sub(r"[|]+", " ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------
# OCR PAGE
# ---------------------------------------------------------

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
        except:
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


# ---------------------------------------------------------
# FIND PRICES
# ---------------------------------------------------------

def find_prices(words):

    prices = []

    for word in words:

        value = parse_price(word["text"])

        if value is None:
            continue

        prices.append({
            **word,
            "price": value
        })

    return prices


# ---------------------------------------------------------
# DISTANCE
# ---------------------------------------------------------

def distance(a, b):

    ax = a["x"] + a["width"] / 2
    ay = a["y"] + a["height"] / 2

    bx = b["x"] + b["width"] / 2
    by = b["y"] + b["height"] / 2

    return (
        (ax - bx) ** 2 +
        (ay - by) ** 2
    ) ** 0.5


# ---------------------------------------------------------
# FIND PRICE PAIRS
# ---------------------------------------------------------

def find_price_pairs(prices):

    pairs = []

    for i in range(len(prices)):

        for j in range(i + 1, len(prices)):

            p1 = prices[i]
            p2 = prices[j]

            # Ignore identical prices
            if p1["price"] == p2["price"]:
                continue

            x_distance = abs(p1["x"] - p2["x"])
            y_distance = abs(p1["y"] - p2["y"])

            # Promotional prices are normally close together
            if x_distance <= 350 and y_distance <= 100:

                high = max(
                    p1["price"],
                    p2["price"]
                )

                low = min(
                    p1["price"],
                    p2["price"]
                )

                # Avoid ridiculous OCR relationships
                if high <= 0:
                    continue

                discount = (
                    (high - low) / high
                ) * 100

                # Discount should normally be meaningful
                if discount < 3:
                    continue

                if discount > 95:
                    continue

                pairs.append({
                    "old_price": high,
                    "current_price": low,
                    "discount_percent": round(discount, 2),
                    "x": min(p1["x"], p2["x"]),
                    "y": min(p1["y"], p2["y"]),
                    "price1": p1,
                    "price2": p2
                })

    return pairs


# ---------------------------------------------------------
# FIND TEXT NEAR PROMOTION
# ---------------------------------------------------------

def get_product_text(words, pair):

    current = pair["price1"]
    old = pair["price2"]

    reference_x = min(
        current["x"],
        old["x"]
    )

    reference_y = min(
        current["y"],
        old["y"]
    )

    candidates = []

    for word in words:

        # Ignore the two prices
        if word is current or word is old:
            continue

        x_distance = abs(
            word["x"] - reference_x
        )

        y_distance = abs(
            word["y"] - reference_y
        )

        # Product text normally sits close to the price
        if x_distance <= 450 and y_distance <= 220:

            text = word["text"]

            if not text:
                continue

            # Ignore obvious page/header information
            upper = text.upper()

            if upper in [
                "SAVERS",
                "SUPERMARKET",
                "PROMOTION",
                "PROMOTIONS"
            ]:
                continue

            candidates.append(word)

    # Sort top-to-bottom and left-to-right
    candidates.sort(
        key=lambda w: (w["y"], w["x"])
    )

    text_parts = []

    for word in candidates:

        text = word["text"]

        # Avoid excessive numeric fragments
        if re.fullmatch(r"\d+", text):
            continue

        text_parts.append(text)

    product_text = " ".join(text_parts)

    product_text = clean_text(product_text)

    return product_text


# ---------------------------------------------------------
# DETECT PROMOTION LABEL
# ---------------------------------------------------------

def detect_promotion(product_text):

    upper = product_text.upper()

    if "VAT ZERO" in upper:
        return "VAT ZERO"

    if "VAT INCL" in upper:
        return "VAT INCL"

    return "Promotion"


# ---------------------------------------------------------
# REMOVE PROMOTION WORDS FROM PRODUCT NAME
# ---------------------------------------------------------

def clean_product_name(text):

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

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip(" -|")


# ---------------------------------------------------------
# REMOVE DUPLICATE PROMOTIONS
# ---------------------------------------------------------

def remove_duplicates(products):

    final_products = []

    for product in products:

        duplicate = False

        for existing in final_products:

            if product["page"] != existing["page"]:
                continue

            same_current = (
                product["current_price"]
                == existing["current_price"]
            )

            same_old = (
                product["old_price"]
                == existing["old_price"]
            )

            if same_current and same_old:
                duplicate = True
                break

        if not duplicate:
            final_products.append(product)

    return final_products


# ---------------------------------------------------------
# PROCESS PAGE
# ---------------------------------------------------------

def process_page(page, page_number):

    print(f"Processing page {page_number}...")

    words = extract_words(page)

    prices = find_prices(words)

    print(
        f"  OCR words: {len(words)}"
    )

    print(
        f"  Prices found: {len(prices)}"
    )

    pairs = find_price_pairs(prices)

    print(
        f"  Price pairs: {len(pairs)}"
    )

    products = []

    for pair in pairs:

        raw_text = get_product_text(
            words,
            pair
        )

        if not raw_text:
            continue

        promotion = detect_promotion(
            raw_text
        )

        product_name = clean_product_name(
            raw_text
        )

        # Skip extremely short OCR fragments
        if len(product_name) < 3:
            continue

        products.append({
            "retailer": "Savers",
            "product_name": product_name,
            "current_price": pair["current_price"],
            "old_price": pair["old_price"],
            "discount_percent": pair["discount_percent"],
            "promotion": promotion,
            "page": page_number
        })

    return products


# ---------------------------------------------------------
# MAIN SCRAPER
# ---------------------------------------------------------

def scrape_savers():

    print("=" * 70)
    print("SAVERS BROCHURE EXTRACTOR")
    print("=" * 70)

    if not os.path.exists(PDF_FILE):

        print(
            f"ERROR: PDF not found: {PDF_FILE}"
        )

        return

    if not os.path.exists(TESSERACT_PATH):

        print(
            "ERROR: Tesseract not found:"
        )

        print(TESSERACT_PATH)

        return

    print()
    print("Opening brochure...")

    document = pymupdf.open(
        PDF_FILE
    )

    print(
        f"Total pages: {len(document)}"
    )

    all_products = []

    for page_index in range(
        len(document)
    ):

        page_number = page_index + 1

        products = process_page(
            document[page_index],
            page_number
        )

        print(
            f"  Products extracted: {len(products)}"
        )

        all_products.extend(products)

    document.close()

    all_products = remove_duplicates(
        all_products
    )

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
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

    print()
    print("=" * 70)
    print("SAVERS EXTRACTION COMPLETE")
    print("=" * 70)

    print(
        f"Total products: {len(all_products)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    scrape_savers()