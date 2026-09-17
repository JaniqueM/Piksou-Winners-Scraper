import csv
import re
from pathlib import Path

import requests
import pymupdf


BROCHURE_URL = (
    "https://www.king-savers.com/wp-content/uploads/2026/07/"
    "KS-EOM-JUL-2026_LR-compressed.pdf"
)

DATA_DIR = Path("data")
BROCHURE_PATH = DATA_DIR / "kingsavers_brochure.pdf"
OUTPUT_FILE = DATA_DIR / "kingsavers_promotions.csv"


def download_brochure():
    DATA_DIR.mkdir(exist_ok=True)

    print("Downloading King Savers brochure...")

    response = requests.get(BROCHURE_URL, timeout=60)
    response.raise_for_status()

    with open(BROCHURE_PATH, "wb") as file:
        file.write(response.content)

    print(f"Brochure saved to: {BROCHURE_PATH}")


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

        print(f"Read page {page_number}/{len(document)}")

    document.close()

    return pages


def is_price(line):
    return re.match(
        r"^Rs\s*[0-9]+(?:\.[0-9]{1,2})?$",
        line,
        re.IGNORECASE
    )


def get_price(line):
    match = re.match(
        r"^Rs\s*([0-9]+(?:\.[0-9]{1,2})?)$",
        line,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


def is_ignored_line(line):
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
        r"^[0-9]+$",
    ]

    for pattern in ignored_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True

    return False

    for pattern in ignored_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True

    return False


def clean_product_name(lines):
    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if is_ignored_line(line):
            continue

        cleaned.append(line)

    return " ".join(cleaned)


def extract_promotions_from_page(page_number, text):

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

        # Ignore general brochure information
        if is_ignored_line(line):
            i += 1
            continue

        # We found a price
        if is_price(line):

            current_price = get_price(line)

            # Check if the next line is an old price
            old_price = None

            if i + 1 < len(lines) and is_price(lines[i + 1]):
                possible_old_price = get_price(lines[i + 1])

                if possible_old_price > current_price:
                    old_price = possible_old_price
                    i += 1

            product_name = clean_product_name(product_lines)

            if product_name:

                discount = None

                if old_price:
                    discount = round(
                        ((old_price - current_price) / old_price) * 100,
                        2
                    )

                promotions.append({
                    "retailer": "King Savers",
                    "product_name": product_name,
                    "current_price": current_price,
                    "old_price": old_price,
                    "discount_percent": discount,
                    "promotion": True,
                    "source": "King Savers Brochure",
                    "page": page_number
                })

            # Reset for the next product
            product_lines = []

            i += 1
            continue

        # Normal text belongs to the current product
        product_lines.append(line)

        i += 1

    return promotions


def remove_duplicates(products):

    unique = {}

    for product in products:

        key = (
            product["product_name"].lower().strip(),
            product["current_price"],
            product["old_price"]
        )

        if key not in unique:
            unique[key] = product

    return list(unique.values())

    unique[key] = product

    return list(unique.values())


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
    print(f"Saved {len(products)} promotions.")
    print(f"CSV: {OUTPUT_FILE}")


def main():

    download_brochure()

    pages = extract_pages()

    all_promotions = []

    for page in pages:

        page_promotions = extract_promotions_from_page(
            page["page"],
            page["text"]
        )

        all_promotions.extend(page_promotions)

        print(
            f"Page {page['page']}: "
            f"{len(page_promotions)} promotions found"
        )

    all_promotions = remove_duplicates(all_promotions)

    save_csv(all_promotions)

    print()
    print("Finished.")


if __name__ == "__main__":
    main()