import os
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from faker import Faker
from tqdm.auto import tqdm
import scraper_backend.proxy
import random

from scraper_backend.utils import progress


def get_all_comics_data(
    download_folder,
    filename,
    comics_title_csv,
):
    titles_info_df = pd.read_csv(comics_title_csv, index_col=0)
    base_url = "https://www.coverbrowser.com"
    mod = 20
    cache = []
    output_path = f"{download_folder}/{filename}.csv"
    if os.path.exists(output_path):
        os.remove(output_path)
    proxy_manager = scraper_backend.proxy.ProxyListManager()
    for row_idx in progress(list(range(len(titles_info_df)))):
        row = titles_info_df.iloc[row_idx]
        url = f"{base_url}{row['page_link']}"
        series_info = get_comic_series_data(url, row["title"], proxy_manager)
        cache.extend(series_info)
        if row_idx % mod == mod - 1:
            pd.DataFrame(cache).to_csv(
                output_path,
                mode="a",
                header=not os.path.exists(output_path),
                index_label="id",
            )
            cache.clear()


def get_comic_series_data(series_url, series_name, proxy_manager) -> None:
    idx = 1
    fake = Faker()
    reached_final_page = False
    miss = 0
    series_info = []
    miss = 0
    while not reached_final_page:
        if miss > 10:
            print(f"cannot reach any of {series_url} subpages.")
            break
        if idx != 1:
            url = series_url + f"/{idx}"
        else:
            url = series_url + "/"
        time.sleep(random.uniform(0.05, 1))
        r = requests.get(
            url,
            proxies={"http": proxy_manager.get_proxy()},
            headers={"User-Agent": fake.user_agent()},
            timeout=5,
            allow_redirects=False,
        )
        if r.status_code == 200:
            page_content = parse_page(r.content, series_name)
            if len(page_content) == 0:
                reached_final_page = True
            series_info.extend(page_content)
        else:
            miss += 1
        idx += 1
    return series_info


def parse_page(page_content, series):
    parsed = BeautifulSoup(page_content, features="html.parser")
    info = []
    for cell in parsed.findAll("p", attrs={"class": "cover"}):
        img_url = cell.find("img")["src"]
        full_title = cell.find("img")["alt"]
        info.append(
            {
                "series": series,
                "full_title": full_title,
                "img_url": img_url,
            }
        )
    return info


if __name__ == "__main__":
    get_all_comics_data("data", "comic-dataset-metadata", "data/comic-titles.csv")
