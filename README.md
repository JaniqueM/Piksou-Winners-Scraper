Winners Mauritius Web Scraper

A Python-based web scraper developed to collect product information from the [Winners Mauritius](https://www.winners.mu) website.

The scraper goes through multiple product categories and their available pages, extracts product information, removes duplicate products, and saves the final results into a CSV file.

Features
* Scrapes products from multiple Winners categories
* Automatically handles pagination
* Extracts:
  * Product ID
  * Product Name
  * SKU
  * Price
  * Product URL
  * Category
* Detects and skips duplicate products
* Handles request timeouts and failed requests
* Saves all unique products to a CSV file
* Displays scraping progress in the terminal

Technologies Used
* Python 3
* Requests – sending HTTP requests
* BeautifulSoup – parsing HTML
* urllib.parse – creating complete URLs
* CSV – storing the scraped data
* Git/GitHub – version control

Project Structure
Piksou/
│
├── category_test.py
├── winners_products.csv
├── .gitignore
└── README.md

How It Works
The scraper follows these main steps:

Start
  ↓
Load Winners category URLs
  ↓
Request category page
  ↓
Check response status
  ↓
Parse HTML with BeautifulSoup
  ↓
Find products
  ↓
Extract product information
  ↓
Check for duplicates
  ↓
Store unique product
  ↓
Move to next page
  ↓
No products found?
  ├── No → Continue scraping
  └── Yes → Move to next category
  ↓
All categories completed
  ↓
Save products to CSV
  ↓
End

Installation
1. Clone the repository
git clone <your-repository-url>
cd Piksou

2. Create a virtual environment
python -m venv .venv

3. Activate the virtual environment
Windows PowerShell:
.venv\Scripts\Activate.ps1

4. Install the required libraries
pip install requests beautifulsoup4

Running the Scraper
Once the virtual environment is activated, run:

python category_test.py

The scraper will begin processing the categories and display its progress in the terminal.

Output
After the scraping process is complete, the data is saved as:
winners_products.csv

The CSV contains the following columns:
| Column       | Description                                 |
| ------------ | ------------------------------------------- |
| `product_id` | Unique Winners product ID                   |
| `name`       | Product name                                |
| `sku`        | Product SKU                                 |
| `price`      | Product price                               |
| `url`        | Product page URL                            |
| `category`   | Category from which the product was scraped |

Duplicate Handling
Some products appear in more than one Winners category.
To prevent duplicate records, the scraper uses a Python `set`

Before adding a product to the results, its product ID is checked against this set.
If the ID has already been scraped, the product is skipped.

Error Handling
The scraper includes basic error handling for network problems.
A timeout is used when making requests

The scraper also handles:
* Request timeouts
* Connection/request failures
* Non-200 HTTP responses
* Empty product pages
This prevents a single failed request from stopping the entire scraping process.

Challenges
The main challenges encountered during development were:
* Understanding the structure of the Winners website
* Identifying the correct HTML elements and CSS selectors
* Implementing reliable pagination
* Determining when there were no more products
* Handling duplicate products across categories
* Dealing with request timeouts
* Processing a large number of categories efficiently

Pagination required significant testing because the scraper needed to correctly move from one page to the next and stop at the appropriate point.

Future Improvements
Possible improvements include:
* Using `requests.Session()` to improve request efficiency
* Adding retry functionality for failed requests
* Saving results periodically
* Improving the pagination system
* Adding more detailed logging
* Improving the overall scraping speed
* Using controlled concurrent requests where appropriate
* Adding a scraping date to the CSV
* Cleaning and standardising scraped price and SKU values

Learning Outcomes
Through this project, I developed practical experience with:
* Python web scraping
* HTTP requests
* HTML structure and CSS selectors
* BeautifulSoup
* Pagination
* Exception handling
* Data collection and CSV files
* Duplicate detection
* Debugging
* Git and GitHub
* Structuring a larger Python script
