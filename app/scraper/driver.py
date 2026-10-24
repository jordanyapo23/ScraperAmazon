import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config


def creer_driver():
    options = Options()
    if config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--lang=fr-FR")
    # Garde le cache du pilote dans le projet si le cache utilisateur n'est pas accessible.
    os.environ.setdefault("SE_CACHE_PATH", str(config.BASE_DIR / ".selenium-cache"))
    return webdriver.Chrome(options=options)
