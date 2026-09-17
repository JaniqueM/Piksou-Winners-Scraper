import pymupdf
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

PDF_FILE = "data/savers_brochure.pdf"
OUTPUT_FILE = "data/savers_ocr_results.txt"


def test_ocr_all_pages():
    document = pymupdf.open(PDF_FILE)

    print(f"Pages found: {len(document)}")
    print("Starting OCR...\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as output:

        for page_number, page in enumerate(document, start=1):

            print(f"Processing page {page_number}/{len(document)}...")

            # Convert PDF page to image
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2)
            )

            # Temporary image path
            image_path = f"data/savers_page_{page_number}.png"

            pixmap.save(image_path)

            # Run OCR
            text = pytesseract.image_to_string(image_path)

            # Save results
            output.write(
                f"\n{'=' * 60}\n"
                f"PAGE {page_number}\n"
                f"{'=' * 60}\n\n"
            )

            output.write(text)

            print(f"Page {page_number} complete.")

    document.close()

    print("\nOCR complete!")
    print(f"Results saved to: {OUTPUT_FILE}")


test_ocr_all_pages()