import argparse
import logging
import multiprocessing as mp
import os
import random
import sys
import time
from functools import partial
from pathlib import Path

import dotenv
import pandas as pd
import requests
from faker import Faker
from PIL import Image
from tqdm.auto import tqdm


def worker(row_idx):
    try:
        row = df.iloc[row_idx]
        download_fn(row)
    except requests.exceptions.RequestException as e:
        logging.info(
            f"Index {row_idx}: {row['img_url']} has error of type"
            f" {e.__class__.__qualname__}."
        )


def init_pool(_df, _download_fn):
    global df, download_fn
    df, download_fn = _df, _download_fn


def create_image_dataset(
    metadata_csv, dataset_location, image_size=250, seed=42, population=0.2
):
    sampled_df = (
        pd.read_csv(metadata_csv, index_col=0)
        .sample(frac=population, random_state=seed)
        .reset_index(drop=True)
    )
    faker = Faker()
    dataset_location = Path(dataset_location)
    sampled_df.to_csv(
        dataset_location / f"sampled_dataset_seed_{seed}_population_{population}.csv",
        index_label=False,
    )
    download_fn = partial(
        download_image,
        dataset_location=dataset_location,
        faker=faker,
        image_size=image_size,
    )
    with mp.Pool(
        initializer=init_pool,
        initargs=(sampled_df, download_fn),
    ) as pool:
        for _ in tqdm(
            pool.imap(worker, sampled_df.index),
            miniters=0.001,
            total=len(sampled_df),
            desc="downloading images",
        ):
            pass


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
    parser.add_argument("--stdout-log", action="store_true")
    parser.add_argument("--random-seed", default=42, type=int)
    parser.add_argument("--image-size", default=250, type=int)
    parser.add_argument("--population", default=0.2, type=float)

    args = parser.parse_args()

    if args.stdout_log:
        stream = sys.stdout
    else:
        stream = sys.stderr

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    random_seed = args.random_seed
    population = args.population
    image_size = args.image_size

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
        stream=stream
        # datefmt='%m-%d %H:%M',
    )
    if os.path.exists("secrets.env"):
        dotenv.load_dotenv("secrets.env")
    create_image_dataset(
        "data/comic-dataset-metadata.csv", "data", image_size, random_seed, population
    )
