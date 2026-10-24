from app.scraper.amazon_scraper import rechercher


class ScrapingController:
    def __init__(self, driver, depot, config_module):
        self.driver = driver
        self.depot = depot
        self.config = config_module

    def lancer(self):
        produits = rechercher(
            self.driver,
            self.config.AMAZON_DOMAIN,
            self.config.SEARCH_QUERY,
            self.config.MAX_PAGES,
            self.config.WAIT_SECONDS,
            self.config.PAGE_DELAY_SECONDS,
            self.config.MAX_PRODUCTS,
        )
        self.depot.remplacer(produits)
        return produits
