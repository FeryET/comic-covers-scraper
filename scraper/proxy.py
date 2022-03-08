from distutils.command.config import config
from typing import List
import requests
import os
import dotenv


secrets = dotenv.dotenv_values("secrets.env")
PROXY_LOCATION = "proxies.txt"


def prepare_proxies():
    with requests.get(secrets["PROXY_DOWNLOAD_URL"]) as r:
        with open(PROXY_LOCATION, "w") as file:
            for url in r.content.splitlines():
                file.write(f"http://{url.decode().strip()}\n")


def list_proxies() -> List[str]:
    with open(PROXY_LOCATION) as proxyfile:
        return [url.strip() for url in proxyfile]