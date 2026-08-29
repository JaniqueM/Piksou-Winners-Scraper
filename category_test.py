import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv


BASE_URL = "https://www.winners.mu"

CATEGORY_PATHS = [
    "/interior-car",
    "/auto-exterieur",
    "/auto-interieur",
    "/entretien-auto",
    "/lubrifiant",
    "/auto--velo",

    "/boucherie",
    "/boucherie-ls",
    "/boucherie-traditionelle",

    "/boulangerie",
    "/pain-ordinaire",
    "/pain-speciaux",
    "/viennoiserie",

    "/bricomaisonjardin",
    "/amenagement-maison",
    "/brico-equipement",
    "/jardinerie",

    "/cartes-telephonie",
    "/cartes-prepayes",

    "/charcuterie",
    "/charcuterie-preemballee",
    "/conservesverrine",
    "/jambon-scisson-sec",
    "/traiteur-ls",

    "/cremerie",
    "/beurre",
    "/fromages-libre-service-2",
    "/margarine",
    "/oeufs",

    "/dph",
    "/beaute",
    "/capillaires",
    "/droguerie",
    "/entretien",
    "/hygiene-papier",
    "/hygiene-parfumerie",
    "/lavage",
    "/parapharmacie",

    "/electro-menager",
    "/cuisson",
    "/encastrable",
    "/entretien-du-linge",
    "/hygiene-beaute",
    "/petit-dejeuner-2",
    "/preparation-alimentaire",
    "/rasage-epilation",
    "/soin-du-linge",

    "/epicerie",
    "/aliments-pour-animaux",
    "/aliments-pour-enfants",
    "/bien-etre-dietetique-bio",
    "/biscuiterie-sucree",
    "/cafes-chicorees",
    "/cereales",
    "/chocolat",
    "/condiments-et-sauces",
    "/fruits-et-legumes",
    "/fleurs-plantes",
    "/fruits-frais",
    "/fruits-sec",
    "/legumes-frais",

    "/souk",
    "/glaces",
    "/detente",
    "/specialites-indiv-a-partager",
    "/vrac",

    "/jouets-loisirs",
    "/camping",
    "/jouet-bebe",
    "/jouet-dete",
    "/jouet-fille",
    "/jouet-garcon",
    "/jouet-mixte",
    "/peche",
    "/sport-dequipe",

    "/librairiepapeteriebagage",
    "/bagage",
    "/librairie",
    "/papeterie",

    "/liquide",
    "/alcools-de-grains",
    "/alcools-et-spiritueux",
    "/aperitifs",
    "/bieres-et-cidres",
    "/boissons-sans-alcool",
    "/champagnes-mousseux",
    "/eaux",
    "/vins-courant",

    "/menage",
    "/articles-menagers",
    "/cadeaux",
    "/couverts-de-table",
    "/cuisson-directe",
    "/cuisson-indirecte",
    "/decoration",
    "/entretien-2",
    "/petit-dejeuner",

    "/micro-bureautique",
    "/calculatrice-organiseur",
    "/consolejeux",
    "/logiciel",
    "/micro-informatique",
    "/support-enregistrement",
    "/telephonie",

    "/patisserie",
    "/biscuits",
    "/cake",
    "/deserts",
    "/entremets",
    "/fete",
    "/gateau-assortis",
    "/genoise",
    "/genoise-vegetarian",

    "/poissonnerie",
    "/mollusquescrustaces",
    "/poissons-frais",
    "/poissonscrustaces-surgele",

    "/porc",
    "/porc-ls",
    "/porc-traditionel",

    "/saurisserie",
    "/marinades",
    "/poissons-fumessales",
    "/produits-canapes",
    "/stand",
    "/charcuterie-coupe",
    "/fromage-coupe",

    "/surgeles",
    "/fruit-et-jus-de-fruits",
    "/garnitures-de-p-de-terre",
    "/legumes-surgeles",
    "/patisserie-et-boule-pate",
    "/plats-cuisines-surgeles",
    "/poissons-fde-merescarg",
    "/potages-et-entrees-surgeles",
    "/traiteur-surgeles",

    "/tabac",
    "/tabac-2",

    "/textile",
    "/accessoires-femmes",
    "/accessoires-hommes",
    "/bijoux",
    "/chapellerie",
    "/chaussure",
    "/confection-bebe",
    "/confection-enfant",
    "/confection-femme",

    "/tvvideohifison",
    "/hifison",
    "/televiseur",
    "/video",

    "/ultra-frais",
    "/cremes-fraiches",
    "/desserts",
    "/fromages-frais",
    "/jus-et-nectar-fruits-frais",
    "/lait-frais",
    "/sauce-frais",
    "/yaourts",

    "/volailles",
    "/volailles-ls",
    "/volailles-traditionelle",
]


CATEGORY_URLS = [
    urljoin(BASE_URL, path)
    for path in CATEGORY_PATHS
]


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

all_products = []

seen_product_ids = set()

for category_url in CATEGORY_URLS:

    print("\n" + "=" * 70)
    print("CATEGORY:", category_url)
    print("=" * 70)

    page = 1

    while True:

        page_url = f"{category_url}?pagenumber={page}"

        print("\nPAGE:", page)
        print("URL:", page_url)

        try:
            response = requests.get(
                page_url,
                headers=headers,
                timeout=20
            )

        except requests.exceptions.Timeout:
            print("Request timed out. Skipping this page.")
            break

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

        print("Status:", response.status_code)

    
        if response.status_code != 200:
            print("Page request failed. Moving to next category.")
            break


        soup = BeautifulSoup(response.text, "html.parser")


        products = soup.select(".product-item")

        print("Products found:", len(products))

       
        if not products:
            print("No more products. Moving to next category.")
            break

        for product in products:

            product_id = product.get("data-productid")

            if product_id in seen_product_ids:
                print("Duplicate product skipped:", product_id)
                continue

            seen_product_ids.add(product_id)

            name_element = product.select_one(".product-title a")
            sku_element = product.select_one(".sku")
            price_element = product.select_one(".actual-price")


            name = (
                name_element.get_text(strip=True)
                if name_element
                else None
            )

            product_url = (
                urljoin(
                    BASE_URL,
                    name_element.get("href")
                )
                if name_element and name_element.get("href")
                else None
            )


            sku = (
                sku_element.get_text(strip=True)
                if sku_element
                else None
            )


            price = (
                price_element.get_text(strip=True)
                if price_element
                else None
            )

            all_products.append({
                "product_id": product_id,
                "name": name,
                "sku": sku,
                "price": price,
                "url": product_url,
                "category": category_url
            })

            print("Product ID:", product_id)
            print("Name:", name)
            print("SKU:", sku)
            print("Price:", price)
            print("URL:", product_url)
            print("-" * 50)

        page += 1

csv_filename = "winners_products.csv"

with open(
    csv_filename,
    "w",
    newline="",
    encoding="utf-8-sig"
) as csvfile:

    fieldnames = [
        "product_id",
        "name",
        "sku",
        "price",
        "url",
        "category"
    ]

    writer = csv.DictWriter(
        csvfile,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(all_products)

print("\n" + "=" * 70)
print("SCRAPING COMPLETE")
print("=" * 70)

print("Total unique products:", len(all_products))
print("CSV file:", csv_filename)