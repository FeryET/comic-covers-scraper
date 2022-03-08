import os
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import scraper.proxy
from fake_useragent import UserAgent
from tqdm.auto import tqdm


def get_all_comics_data(
    download_folder,
    filename,
    comics_title_csv,
):
    scraper.proxy.prepare_proxies()
    titles_info_df = pd.read_csv(comics_title_csv, index_col=0)
    base_url = "https://www.coverbrowser.com"
    proxy_idx = 0
    mod = 20
    cache = []
    output_path = f"{download_folder}/{filename}.csv"
    if os.path.exists(output_path):
        os.remove(output_path)
    for row_idx in tqdm(titles_info_df.index):
        row = titles_info_df.iloc[row_idx]
        series_info, proxy_idx = get_comic_series_data(
            f"{base_url}{row['page_link']}", row["title"], proxy_idx
        )
        cache.extend(series_info)
        if row_idx % mod == mod - 1:
            pd.DataFrame(cache).to_csv(
                output_path, mode="a", header=not os.path.exists(output_path)
            )
            cache.clear()


def get_comic_series_data(series_url, series_name, proxy_idx) -> None:
    idx = 1
    ua = UserAgent()
    reached_final_page = False
    miss = 0
    series_info = []
    proxies = scraper.proxy.list_proxies()
    while not reached_final_page:
        if idx != 1:
            url = series_url + f"/{idx}"
        else:
            url = series_url + "/"
        while True:
            time.sleep(0.05)
            r = requests.get(
                url,
                proxies={"http": proxies[proxy_idx]},
                headers={"User-Agent": ua.random},
                allow_redirects=True,
            )
            if r.status_code == 200:
                break
            else:
                proxy_idx += 1
                miss += 1
            if miss >= 10:
                scraper.proxy.prepare_proxies()
                proxies = scraper.proxy.list_proxies()
                proxy_idx = 0
                miss = 0
        page_content = parse_page(r.content, series_name)
        idx += 1
        if len(page_content) == 0:
            reached_final_page = True
            break
        else:
            series_info.extend(page_content)
    return series_info, proxy_idx


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
    get_all_comics_data("data", "comic-dataset-metadta", "data/comic-titles.csv")
