# -*- coding: utf-8 -*-
"""
Created on Thu May 30 15:52:50 2024

@author: Lhanh
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL for constructing full URLs
base_url = "https://www.politie.nl"


# Function to scrape a single page and extract data
def scrape_page(page_number):
    url = (
        f"{base_url}/gezocht-en-vermist/cold-cases-de-zaken?page={page_number}"
    )
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the webpage for page {page_number}.")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    ul_element = soup.find(
        "ul",
        class_="small-block-grid-1 medium-block-grid-2 large-block-grid-3 imagelist",
    )

    if not ul_element:
        print(f"No data found on page {page_number}.")
        return []

    a_tags = ul_element.find_all("a", class_="imagelistlink")
    hrefs = [a["href"] for a in a_tags]
    data_list = []

    for href in hrefs:
        item_url = base_url + href
        item_response = requests.get(item_url)

        if item_response.status_code == 200:
            item_soup = BeautifulSoup(item_response.content, "html.parser")
            metadata_dl = item_soup.find("dl", class_="metadata-dl")

            if metadata_dl:
                data = {}
                dt_elements = metadata_dl.find_all("dt")
                dd_elements = metadata_dl.find_all("dd")

                for dt, dd in zip(dt_elements, dd_elements):
                    key = (
                        dt.get_text(strip=True)
                        .replace(":", "")
                        .lower()
                        .replace(" ", "_")
                    )
                    value = dd.get_text(strip=True)
                    data[key] = value

                data_list.append(data)

    return data_list


# Main script to scrape all pages from 1 to 16 and merge data
all_data = []
for page_number in range(1, 16):
    page_data = scrape_page(page_number)
    all_data.extend(page_data)

df = pd.DataFrame(all_data)

output_file = "cold_cases.xlsx"

df.to_excel(output_file, index=True)
