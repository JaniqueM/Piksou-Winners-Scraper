import pymupdf

PDF_FILE = "data/savers_brochure.pdf"
OUTPUT_FILE = "data/savers_page_2.png"

document = pymupdf.open(PDF_FILE)

page = document[1]

pixmap = page.get_pixmap(
    matrix=pymupdf.Matrix(2, 2)
)

pixmap.save(OUTPUT_FILE)

document.close()

print(f"Saved page image to: {OUTPUT_FILE}")