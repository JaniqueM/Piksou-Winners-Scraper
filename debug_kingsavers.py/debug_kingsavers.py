import pymupdf

PDF_FILE = "data/kingsavers_brochure.pdf"

document = pymupdf.open(PDF_FILE)

page = document[0]
text = page.get_text("text")

lines = [line.strip() for line in text.splitlines() if line.strip()]

for number, line in enumerate(lines, start=1):
    print(f"{number}: {line}")

document.close()