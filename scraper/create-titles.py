from pathlib import Path
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import string
import scraper.proxy
from fake_useragent import UserAgent
import re


def create_titles_csv_file(download_folder: str, filename: str) -> None:
    alphabet = ["0-9"] + list(string.ascii_lowercase)
    base_url = "https://www.coverbrowser.com/a-z"
    scraper.proxy.prepare_proxies()
    proxies = scraper.proxy.list_proxies()
    miss = 0
    proxy_idx = 0
    ua = UserAgent()
    titles_info = []
    for char in alphabet:
        successful_request = False
        row_info = None
        while not successful_request:
            time.sleep(0.1)
            r = requests.get(
                f"{base_url}/{char}/",
                proxies={"http": proxies[proxy_idx]},
                headers={"User-Agent": ua.random},
            )
            if r.status_code == 200:
                successful_request = True
                row_info = parse_title_page(r.content)
                print(row_info)
                break
            else:
                proxy_idx += 1
                miss += 1
        if miss > 10:
            scraper.proxy.prepare_proxies()
            miss = 0
            proxy_idx = 0

        if row_info is None:
            print(f"Issue in character: {char}")
            continue
        titles_info.extend(row_info)

    pd.DataFrame(titles_info).to_csv(Path(download_folder) / f"{filename}.csv")


def parse_title_page(content):
    pattern = re.compile("/covers/.+")
    table = []
    parsed = BeautifulSoup(content, features="html.parser")
    for link in parsed.findAll("a"):
        if link.has_attr("href") and pattern.match(link["href"]):
            table.append({"title": link.text, "page_link": link["href"]})
    print(table)
    return table


if __name__ == "__main__":
    create_titles_csv_file("data", "comic-titles")
