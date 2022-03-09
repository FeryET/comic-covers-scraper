from distutils.command.config import config
from typing import List
import requests
import os
import random

PROXY_LOCATION = "proxies.txt"


class ProxyListManager:
    def __init__(self):
        self.prepare()

    def prepare(self):
        self.n = 0
        with requests.get(os.environ["MORPH_PROXY_URL"]) as r:
            self.proxies = [
                f"http://{url.decode().strip()}\n" for url in r.content.splitlines()
            ]
        random.shuffle(self.proxies)

    def __len__(self):
        return len(self.proxies)

    def get_proxy(self):
        if self.n >= len(self):
            self.prepare()
        item = self.proxies[self.n]
        self.n += 1
        return item
