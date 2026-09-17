import requests
import pymupdf
from pathlib import Path


BROCHURE_URL = (
    "https://savers.mu/wp-content/uploads/2025/06/"
    "Promo-21-june-17-july-2025.pdf"
)

DATA_DIR = Path("data")
PDF_FILE = DATA_DIR / "savers_brochure.pdf"


def download_brochure():
    DATA_DIR.mkdir(exist_ok=True)

    print("Downloading Savers brochure...")

    response = requests.get(
        BROCHURE_URL,
        timeout=60
    )

    response.raise_for_status()

    with open(PDF_FILE, "wb") as file:
        file.write(response.content)

    print(f"Saved to: {PDF_FILE}")


def inspect_brochure():

    print("Opening brochure...")

    document = pymupdf.open(PDF_FILE)

    print(f"Pages: {len(document)}")
    print()

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")
        images = page.get_images(full=True)

        text_characters = len(text.strip())
        image_count = len(images)

        print(
            f"Page {page_number}: "
            f"{text_characters} text characters, "
            f"{image_count} images"
        )

    document.close()


def main():

    download_brochure()

    inspect_brochure()

    print()
    print("Inspection complete.")


if __name__ == "__main__":
    main()