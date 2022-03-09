import dotenv
from scraper_backend.create_image_dataset_metadata import get_all_comics_data
from scraper_backend.create_titles import create_titles_csv_file
import pandas as pd
import scraperwiki
import os
import logging

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
#     # datefmt='%m-%d %H:%M',
# )

if os.path.exists("secrets.env"):
    dotenv.load_dotenv("secrets.env")
    print("Loaded environment variables.")

create_titles_csv_file("data", "comic-titles")
get_all_comics_data("data", "comic-dataset-metadata", "data/comic-titles.csv")


data = pd.read_csv("data/comic-dataset-metadata.csv").to_dict("records")
scraperwiki.sqlite.save(unique_keys=["id"], data=data)
