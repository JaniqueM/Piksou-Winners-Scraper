import csv
import re
from pathlib import Path

import requests
import pymupdf


# ============================================================
# CONFIG
# ============================================================

BROCHURE_URL = (
    "https://www.king-savers.com/wp-content/uploads/2026/07/"
    "KS-EOM-JUL-2026_LR-compressed.pdf"
)

DATA_DIR = Path("data")
BROCHURE_PATH = DATA_DIR / "kingsavers_brochure.pdf"
OUTPUT_FILE = DATA_DIR / "kingsavers_promotions.csv"


# ============================================================
# DOWNLOAD BROCHURE
# ============================================================

def download_brochure():

    DATA_DIR.mkdir(exist_ok=True)

    print("Downloading King Savers brochure...")

    response = requests.get(
        BROCHURE_URL,
        timeout=60
    )

    response.raise_for_status()

    with open(BROCHURE_PATH, "wb") as file:
        file.write(response.content)

    print(f"Brochure saved to: {BROCHURE_PATH}")


# ============================================================
# EXTRACT TEXT FROM ALL PAGES
# ============================================================

def extract_pages():

    print("Opening brochure...")

    document = pymupdf.open(BROCHURE_PATH)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        pages.append({
            "page": page_number,
            "text": text
        })

        print(
            f"Read page {page_number}/{len(document)}"
        )

    document.close()

    return pages


# ============================================================
# PRICE EXTRACTION
# ============================================================

def extract_prices(text):

    pattern = r"Rs\s*([0-9]+(?:\.[0-9]{1,2})?)"

    matches = re.findall(
        pattern,
        text,
        re.IGNORECASE
    )

    prices = []

    for match in matches:

        try:
            prices.append(float(match))

        except ValueError:
            continue

    return prices


# ============================================================
# FIND PROMOTIONS
# ============================================================

def extract_promotions_from_page(page_number, text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    promotions = []

    i = 0

    while i < len(lines):

        line = lines[i]

        # Look for a price
        price_match = re.match(
            r"Rs\s*([0-9]+(?:\.[0-9]{1,2})?)",
            line,
            re.IGNORECASE
        )

        if price_match:

            current_price = float(
                price_match.group(1)
            )

            # Look ahead for another price
            next_price = None

            if i + 1 < len(lines):

                next_match = re.match(
                    r"Rs\s*([0-9]+(?:\.[0-9]{1,2})?)",
                    lines[i + 1],
                    re.IGNORECASE
                )

                if next_match:
                    next_price = float(
                        next_match.group(1)
                    )

            # If two prices exist, assume:
            # first = promotional price
            # second = original price

            if next_price and next_price > current_price:

                product_name = "Unknown Product"

                # Look backwards for product name
                previous_lines = []

                j = i - 1

                while j >= 0 and len(previous_lines) < 5:

                    candidate = lines[j]

                    if not re.match(
                        r"Rs\s*",
                        candidate,
                        re.IGNORECASE
                    ):

                        previous_lines.append(
                            candidate
                        )

                    j -= 1

                if previous_lines:

                    product_name = " ".join(
                        reversed(previous_lines)
                    )

                discount = round(
                    (
                        (next_price - current_price)
                        / next_price
                    ) * 100,
                    2
                )

                promotions.append({
                    "retailer": "King Savers",
                    "product_name": product_name,
                    "current_price": current_price,
                    "old_price": next_price,
                    "discount_percent": discount,
                    "promotion": True,
                    "source": "King Savers Brochure",
                    "page": page_number
                })

                i += 2
                continue

        i += 1

    return promotions


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(products):

    unique = {}

    for product in products:

        key = (
            product["product_name"].lower().strip(),
            product["current_price"],
            product["old_price"]
        )

        unique[key] = product

    return list(unique.values())


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(products):

    if not products:

        print("No promotions found.")

        return

    fieldnames = [
        "retailer",
        "product_name",
        "current_price",
        "old_price",
        "discount_percent",
        "promotion",
        "source",
        "page"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(products)

    print()
    print(
        f"Saved {len(products)} promotions."
    )

    print(
        f"CSV: {OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # 1. Download
    download_brochure()

    # 2. Read ALL pages
    pages = extract_pages()

    # 3. Extract promotions
    all_promotions = []

    for page in pages:

        page_promotions = extract_promotions_from_page(
            page["page"],
            page["text"]
        )

        all_promotions.extend(
            page_promotions
        )

        print(
            f"Page {page['page']}: "
            f"{len(page_promotions)} promotions found"
        )

    # 4. Deduplicate
    all_promotions = remove_duplicates(
        all_promotions
    )

    # 5. Save
    save_csv(all_promotions)

    print()
    print("Finished.")


if __name__ == "__main__":
    main()