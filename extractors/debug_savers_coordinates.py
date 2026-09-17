import pymupdf
import pytesseract
from pytesseract import Output
from PIL import Image
import io
import re


# --------------------------------------------------
# TESSERACT
# --------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# --------------------------------------------------
# FILE
# --------------------------------------------------

PDF_FILE = "data/savers_brochure.pdf"

# Page 2
PAGE_NUMBER = 1


# --------------------------------------------------
# PRICE DETECTION
# --------------------------------------------------

def is_price(text):

    text = text.strip()

    # Examples:
    # 72.00
    # 116.00
    # 314.00
    # 5.00

    pattern = r"^\d{1,4}\.\d{2}$"

    return bool(re.match(pattern, text))


# --------------------------------------------------
# MAIN DEBUGGER
# --------------------------------------------------

def inspect_page():

    print("=" * 70)
    print("SAVERS PRICE COORDINATE DEBUGGER")
    print("=" * 70)

    document = pymupdf.open(PDF_FILE)

    print(f"PDF opened successfully.")
    print(f"Total pages: {len(document)}")

    page = document[PAGE_NUMBER]

    print(f"\nProcessing page {PAGE_NUMBER + 1}...")

    # Render page at 2x resolution
    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2)
    )

    image = Image.open(
        io.BytesIO(
            pixmap.tobytes("png")
        )
    )

    print(f"Image size: {image.size}")

    # --------------------------------------------------
    # OCR
    # --------------------------------------------------

    data = pytesseract.image_to_data(
        image,
        output_type=Output.DICT
    )

    # --------------------------------------------------
    # BUILD OCR WORD LIST
    # --------------------------------------------------

    words = []

    for i, text in enumerate(data["text"]):

        text = text.strip()

        if not text:
            continue

        words.append({
            "text": text,
            "x": data["left"][i],
            "y": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i],
            "confidence": data["conf"][i]
        })

    # --------------------------------------------------
    # FIND PRICES
    # --------------------------------------------------

    prices = [
        word
        for word in words
        if is_price(word["text"])
    ]

    print("\n")
    print("=" * 70)
    print("PRICE CANDIDATES")
    print("=" * 70)

    if not prices:
        print("No price candidates found.")

    else:

        for price in prices:

            print(
                f"\nPRICE: Rs {price['text']}"
                f" | X={price['x']}"
                f" | Y={price['y']}"
            )

            print("Nearby text:")

            nearby = []

            for word in words:

                if word is price:
                    continue

                x_distance = abs(
                    word["x"] - price["x"]
                )

                y_distance = abs(
                    word["y"] - price["y"]
                )

                # Nearby area
                if (
                    x_distance <= 180
                    and y_distance <= 100
                ):
                    nearby.append(word)

            # Sort by vertical position first
            nearby.sort(
                key=lambda item: (
                    item["y"],
                    item["x"]
                )
            )

            for word in nearby:

                print(
                    f"   {word['text']:25}"
                    f" X={word['x']:4}"
                    f" Y={word['y']:4}"
                    f" CONF={word['confidence']}"
                )

    # --------------------------------------------------
    # CLOSE
    # --------------------------------------------------

    document.close()

    print("\n")
    print("=" * 70)
    print("DEBUGGING COMPLETE")
    print("=" * 70)


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    inspect_page()