import sys

import config
from app.controllers.scraping_controller import ScrapingController
from app.models.depot import Depot
from app.scraper.amazon_scraper import AccesRefuseError
from app.scraper.driver import creer_driver
from app.views.console_view import afficher_resultat
from app.views.export_view import exporter_csv


def main():
    driver = creer_driver()
    try:
        produits = ScrapingController(driver, Depot(config.DB_PATH), config).lancer()
        csv_path = exporter_csv(produits, config.EXPORT_DIR)
        afficher_resultat(produits, csv_path)
    except AccesRefuseError as error:
        print("Arrêt : {}".format(error), file=sys.stderr)
        return 2
    finally:
        if config.KEEP_BROWSER_OPEN:
            try:
                input("\nChrome reste ouvert. Appuie sur Entrée pour le fermer... ")
            except EOFError:
                pass
        driver.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
