from distutils.command.config import config
from typing import List
import requests
import os
import random

PROXY_LOCATION = "proxies.txt"


def prepare_proxies():
    with requests.get(os.environ["MORPH_PROXY_URL"]) as r:
        with open(PROXY_LOCATION, "w") as file:
            for url in r.content.splitlines():
                file.write(f"http://{url.decode().strip()}\n")


def shuffle_proxies() -> List[str]:
    with open(PROXY_LOCATION) as proxyfile:
        proxies = [url.strip() for url in proxyfile]
        random.shuffle(proxies)
        return proxies


def get_proxies():
    prepare_proxies()
    return shuffle_proxies()
