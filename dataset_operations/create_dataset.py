from http.client import HTTPException
import logging
import dotenv
from faker import Faker
from proxy import ProxyListManager
import pandas as pd
from PIL import Image
import requests
from utils import progress
from pathlib import Path


def create_image_dataset(metadata_csv, dataset_location, image_size=250):
    df = pd.read_csv(metadata_csv)
    proxy_manager = ProxyListManager()
    faker = Faker()
    dataset_location = Path(dataset_location)
    for row_idx in progress(df.index, interval=0.001):
        try:
            row = df.iloc[row_idx]
            download_image(row, dataset_location, proxy_manager, faker, image_size)
        except HTTPException as e:
            logging.info(
                f"Index {row_idx}: {row['img_url']} has error of type"
                f" {e.__class__.__qualname__}."
            )


def download_image(row, dataset_location, proxy_manager, faker, image_size):
    fpath: Path = dataset_location / Path(row["img_url"][1:])
    if fpath.exists():
        return
    fpath.parent.mkdir(exist_ok=True, parents=True)
    base_url = "https://coverbrowser.com"
    url = f"{base_url}{row['img_url']}"
    with requests.get(
        url,
        proxies={"http": proxy_manager.get_proxy()},
        headers={"User-Agent": faker.user_agent()},
        stream=True,
    ) as r:
        print(r.status_code)
        image = Image.open(r.raw)
        image.thumbnail((image_size, image_size))
        image.save(fpath)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
        # datefmt='%m-%d %H:%M',
    )
    dotenv.load_dotenv("secrets.env")
    create_image_dataset("data/comic-dataset-metadata.csv", "data")
