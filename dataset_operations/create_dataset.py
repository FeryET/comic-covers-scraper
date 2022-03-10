import logging
import random
import time
import dotenv
from faker import Faker
import pandas as pd
from PIL import Image
import requests
from utils import progress
from pathlib import Path
import argparse


def create_image_dataset(
    metadata_csv, dataset_location, image_size=250, seed=42, population=0.1
):
    sampled_df = (
        pd.read_csv(metadata_csv)
        .sample(frac=population, random_state=seed)
        .reset_index(drop=True)
    )
    faker = Faker()
    dataset_location = Path(dataset_location)
    sampled_df.to_csv(
        dataset_location / f"sampled_dataset_seed_{seed}_population_{population}.csv",
        index_label=False,
    )
    for row_idx in progress(sampled_df.index, interval=0.001):
        try:
            row = sampled_df.iloc[row_idx]
            download_image(row, dataset_location, faker, image_size)
        except requests.exceptions.RequestException as e:
            logging.info(
                f"Index {row_idx}: {row['img_url']} has error of type"
                f" {e.__class__.__qualname__}."
            )


def download_image(row, dataset_location, faker, image_size):
    fpath: Path = dataset_location / Path(row["img_url"][1:])
    if fpath.exists():
        return
    fpath.parent.mkdir(exist_ok=True, parents=True)
    base_url = "https://coverbrowser.com"
    url = f"{base_url}{row['img_url']}"
    with requests.get(
        url,
        headers={"User-Agent": faker.user_agent()},
        stream=True,
        allow_redirects=True,
        timeout=(1, 5),
    ) as r:
        if r.status_code == 200:
            image = Image.open(r.raw)
            image.thumbnail((image_size, image_size), resample=Image.NEAREST)
            image.save(fpath)
        else:
            logging.info(f"Cannot download {url}. status code: {r.status_code}")

        time.sleep(random.uniform(0.05, 0.5))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
        # datefmt='%m-%d %H:%M',
    )
    dotenv.load_dotenv("secrets.env")
    create_image_dataset("data/comic-dataset-metadata.csv", "data")
