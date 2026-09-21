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
OUTPUT_FILE = "data/savers_price_candidates.csv"

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================
# PRICE DETECTION
# ============================================================

def is_price(text):
    """
    Check whether an OCR word looks like a price.

    Examples:
        5.00
        38.00
        72.00
        116.00
        314.00
    """

    text = text.strip()

    return bool(
        re.fullmatch(r"\d{1,4}\.\d{2}", text)
    )


# ============================================================
# OCR A SINGLE PAGE
# ============================================================

def process_page(page, page_number):

    print(f"Processing page {page_number}...")

    # --------------------------------------------------------
    # Convert PDF page to image
    # --------------------------------------------------------

    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2)
    )

    image = Image.open(
        io.BytesIO(
            pixmap.tobytes("png")
        )
    )

    # --------------------------------------------------------
    # Run Tesseract OCR
    # --------------------------------------------------------

    data = pytesseract.image_to_data(
        image,
        output_type=Output.DICT
    )

    prices = []

    # --------------------------------------------------------
    # Find prices
    # --------------------------------------------------------

    for i, text in enumerate(data["text"]):

        text = text.strip()

        if not text:
            continue

        if is_price(text):

            prices.append({
                "retailer": "Savers",
                "price": float(text),
                "page": page_number,
                "x": data["left"][i],
                "y": data["top"][i],
                "confidence": data["conf"][i]
            })

    print(
        f"  Found {len(prices)} price candidates"
    )

    return prices


# ============================================================
# MAIN SCRAPER
# ============================================================

def scrape_savers():

    print("=" * 70)
    print("SAVERS SCRAPER")
    print("=" * 70)

    # --------------------------------------------------------
    # Check PDF
    # --------------------------------------------------------

    if not os.path.exists(PDF_FILE):

        print()
        print("ERROR:")
        print(f"Could not find: {PDF_FILE}")
        print()

        return

    # --------------------------------------------------------
    # Open PDF
    # --------------------------------------------------------

    print()
    print("Opening Savers brochure...")

    document = pymupdf.open(PDF_FILE)

    print(
        f"Brochure opened successfully."
    )

    print(
        f"Total pages: {len(document)}"
    )

    # --------------------------------------------------------
    # Process every page
    # --------------------------------------------------------

    all_prices = []

    for page_index in range(len(document)):

        page_number = page_index + 1

        page = document[page_index]

        prices = process_page(
            page,
            page_number
        )

        all_prices.extend(prices)

    document.close()

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    print()
    print("Saving results...")

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
            "price",
            "page",
            "x",
            "y",
            "confidence"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(all_prices)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("SAVERS SCRAPER COMPLETE")
    print("=" * 70)

    print(
        f"Total price candidates: {len(all_prices)}"
    )

    print(
        f"CSV saved to: {OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    scrape_savers()