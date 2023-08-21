# pip install requests
# pip install beautifulsoup4
# pip install lxml

import requests
from bs4 import BeautifulSoup
import csv
import time

# Part 1: Scrape product details from listing pages
base_url = "https://www.amazon.in/s"
search_query = "bags"
page_count = 160

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

product_data = []

for page in range(1, page_count + 1):
    params = {
        "k": search_query,
        "page": page
    }
    response = requests.get(base_url, headers=headers, params=params)
    soup = BeautifulSoup(response.content, "html.parser")

    product_containers = soup.find_all("div", {"data-component-type": "s-search-result"})
    for container in product_containers:
        product_url = container.find("a", class_="a-link-normal")["href"]
        product_name = container.find("span", class_="a-text-normal").text
        product_price = container.find("span", class_="a-price").find("span", class_="a-offscreen").text
        product_rating = container.find("span", class_="a-icon-alt").text.split()[0]
        num_reviews = container.find("span", class_="a-size-base").text.split()[0]

        product_data.append({
            "Product URL": "https://www.amazon.in" + product_url,
            "Product Name": product_name,
            "Product Price": product_price,
            "Rating": product_rating,
            "Number of Reviews": num_reviews
        })

    time.sleep(2)  # To avoid overloading the server

# Part 2: Scrape additional product details from individual product pages

for product in product_data:
    product_url = product["Product URL"]
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    
    product_description = soup.find("meta", {"name": "description"})
    asin = soup.find("input", {"id": "ASIN"})
    manufacturer = soup.find("a", {"id": "bylineInfo"})

    product.update({
        "Description": product_description["content"] if product_description else "N/A",
        "ASIN": asin["value"] if asin else "N/A",
        "Product Description": soup.find("div", {"id": "productDescription"}).get_text(strip=True)
                              if soup.find("div", {"id": "productDescription"}) else "N/A",
        "Manufacturer": manufacturer.text.strip() if manufacturer else "N/A"
    })

csv_filename = "amazon_product_data.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
    fieldnames = ["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews",
                  "Description", "ASIN", "Product Description", "Manufacturer"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(product_data)

print("Scraping and CSV export complete.")
