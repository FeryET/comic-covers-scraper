from pathlib import Path
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import string
from faker import Faker
import re
import random

from sqlalchemy import desc
import scraper_backend.proxy
from tqdm.auto import tqdm

from scraper_backend.utils import progress


def create_titles_csv_file(download_folder: str, filename: str) -> None:
    alphabet = ["0-9"] + list(string.ascii_lowercase)
    base_url = "https://www.coverbrowser.com/a-z"
    fake = Faker()
    titles_info = []
    proxy_manager = scraper_backend.proxy.ProxyListManager()
    for char in progress(alphabet):
        time.sleep(random.uniform(0.05, 0.5))
        r = requests.get(
            f"{base_url}/{char}/",
            proxies={"http": proxy_manager.get_proxy()},
            headers={"User-Agent": fake.user_agent()},
        )
        if r.status_code == 200:
            titles_info.extend(parse_title_page(r.content))
        else:
            print(f"Issue in character: {char}")
            continue

    pd.DataFrame(titles_info).to_csv(Path(download_folder) / f"{filename}.csv")


def parse_title_page(content):
    pattern = re.compile("/covers/.+")
    table = []
    parsed = BeautifulSoup(content, features="html.parser")
    for link in parsed.findAll("a"):
        if link.has_attr("href") and pattern.match(link["href"]):
            table.append({"title": link.text, "page_link": link["href"]})
    return table


if __name__ == "__main__":
    create_titles_csv_file("data", "comic-titles")
