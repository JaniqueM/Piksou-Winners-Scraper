# PikSou – Retail Promotion Web Scraper
PikSou is a Python-based web scraping project designed to collect product and promotion information from Mauritius retailers.

The project uses a shared scraping engine with separate retailer-specific scrapers.

# Project Structure
PikSou/
│
├── engine/
│   └── scraper.py
│
├── scrapers_plugins/
│   ├── base_scraper.py
│   ├── winners_scraper.py
│   ├── kingsavers_scraper.py
│   └── savers_scraper.py
│
├── runners/
│   ├── runner_engine_winners.py
│   ├── runner_engine_kingsavers.py
│   └── runner_engine_savers.py
│
├── models/
│   └── product.py
│
├── exporters/
│   └── csv_exporter.py
│
├── data/
│
├── requirements.txt
└── README.md

## How the Scraper Works
The project is divided into three main parts:

1. Scraping Engine
The engine provides the common functionality needed to run the scrapers.

2. Retailer Scrapers
Each retailer has its own scraper because different websites and brochures have different structures.
Current scrapers:
* Winners
* King Savers
* Savers

3. Runners
A runner starts one specific retailer scraper and exports its results.
This means the retailers are kept separate and can be run independently.

#Installation
Clone or download the project and open the project folder in the terminal.
Create a virtual environment:

bash
python -m venv .venv

Activate it on Windows:
.venv\Scripts\activate

Install the required packages:
pip install -r requirements.txt

#Running a Scraper
Run the retailer you want from the project folder.

#Winners
python runners/runner_engine_winners.py

#King Savers
python runners/runner_engine_kingsavers.py

#Savers
python runners/runner_engine_savers.py
If your runner files are currently in the main project folder instead of the `runners` folder, use:

python runner_engine_winners.py
python runner_engine_kingsavers.py
python runner_engine_savers.py

#Output
The scraper extracts information such as:
* Product name
* SKU, when available
* Current price
* Old price, when available
* Discount percentage
* Promotion status
* Retailer/source
* Brochure page, when applicable
* Product URL, when available
The results are exported as CSV files inside the `data` folder.

#Different Data Sources
The scrapers can work with different types of retailer sources.

#Winners
Winners is scraped directly from its website.
Website
   ↓
Scraper
   ↓
Product data
   ↓
CSV

#King Savers
King Savers uses a promotional PDF brochure.
PDF Brochure
   ↓
PDF Extraction
   ↓
Product data
   ↓
CSV

#Savers
Savers uses a promotional brochure and OCR where required.
PDF Brochure
   ↓
OCR
   ↓
Product data
   ↓
CSV

#Important
Each retailer scraper is independent.
To add another retailer, create a new scraper inside:

scrapers_plugins/

and create a corresponding runner.

The existing engine and product model can then be reused.

#Basic Workflow
Choose Retailer
      ↓
Run Retailer's Runner
      ↓
Retailer Scraper Collects Data
      ↓
Data Converted to Product Objects
      ↓
CSV Exporter
      ↓
CSV File in data/

#Technologies Used
* Python
* Requests
* BeautifulSoup
* PyMuPDF
* Tesseract OCR
* Pytesseract
* Pandas
* Git/GitHub
