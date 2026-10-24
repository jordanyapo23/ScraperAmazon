from typing import List, Optional
from urllib.parse import quote_plus
import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.models.produit import Produit


class AccesRefuseError(RuntimeError):
    pass


def _texte(element, selector: str) -> Optional[str]:
    try:
        for match in element.find_elements(By.CSS_SELECTOR, selector):
            value = (
                match.get_attribute("content")
                or match.get_attribute("textContent")
                or match.get_attribute("aria-label")
                or match.text
                or ""
            ).strip()
            if value:
                return value
        return None
    except WebDriverException:
        return None


def _premier_texte(driver, selectors: List[str]) -> Optional[str]:
    for selector in selectors:
        value = _texte(driver, selector)
        if value:
            return value
    return None


SELECTEURS_PRIX = [
    "#corePriceDisplay_desktop_feature_div .priceToPay .a-offscreen",
    "#corePriceDisplay_desktop_feature_div .a-offscreen",
    "#corePrice_feature_div .a-offscreen",
    "#corePrice_desktop .a-offscreen",
    "#apex_desktop .a-price .a-offscreen",
    "#priceblock_ourprice, #priceblock_dealprice, #price_inside_buybox",
    ".reinventPricePriceToPayMargin .a-offscreen",
    ".priceToPay .a-offscreen",
    "#aod-price-1 .a-offscreen",
    "[data-a-color='price'] .a-offscreen",
    "span.a-price span.a-offscreen",
    "meta[property='product:price:amount']",
    "meta[itemprop='price']",
]
SELECTEURS_NOTE = [
    "#acrPopover .a-icon-alt",
    "#averageCustomerReviews .a-icon-alt",
    "i[data-hook='average-star-rating'] span.a-icon-alt",
    "span[data-hook='rating-out-of-text']",
    "span.a-icon-alt",
    "meta[itemprop='ratingValue']",
]
SELECTEURS_AVIS = [
    "#acrCustomerReviewText",
    "#acrCustomerReviewLink #acrCustomerReviewText",
    "span[data-hook='total-review-count']",
    "a[href*='#customerReviews'] span.a-size-base",
    "span.a-size-base.s-underline-text",
    "meta[itemprop='reviewCount']",
]


def _completer_depuis_fiches(driver, produits: List[Produit], wait_seconds: int) -> None:
    """Va sur les fiches produit pour compléter les données absentes des résultats."""
    a_completer = [p for p in produits if not (p.prix and p.note and p.avis)]
    if not a_completer:
        return

    onglet_recherche = driver.current_window_handle
    onglet_fiche = None
    try:
        driver.switch_to.new_window("tab")
        onglet_fiche = driver.current_window_handle
        for index, produit in enumerate(a_completer, start=1):
            # L’URL canonique évite les liens de suivi de la page de résultats.
            url = "https://{}/dp/{}".format(produit.marketplace, produit.asin)
            try:
                driver.get(url)
                wait = WebDriverWait(driver, min(wait_seconds, 8))
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                _gerer_consentement(driver, wait)
                if not produit.prix:
                    try:
                        WebDriverWait(driver, 4).until(
                            lambda browser: _premier_texte(browser, SELECTEURS_PRIX)
                        )
                    except TimeoutException:
                        pass
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                if "captcha" in page_text or "robot check" in page_text:
                    print("Vérification Amazon détectée : arrêt de la collecte des détails produit.")
                    break

                produit.prix = produit.prix or _premier_texte(driver, SELECTEURS_PRIX)
                produit.note = produit.note or _premier_texte(driver, SELECTEURS_NOTE)
                produit.avis = produit.avis or _premier_texte(driver, SELECTEURS_AVIS)
            except (TimeoutException, WebDriverException) as error:
                print("Détails indisponibles pour {} : {}".format(produit.asin, error.__class__.__name__))
            if index < len(a_completer):
                time.sleep(0.5)
    except WebDriverException as error:
        print("Impossible d’ouvrir un onglet pour les détails : {}".format(error.__class__.__name__))
    finally:
        if onglet_fiche:
            try:
                driver.switch_to.window(onglet_fiche)
                driver.close()
                driver.switch_to.window(onglet_recherche)
            except WebDriverException:
                pass


def _gerer_consentement(driver, wait) -> None:
    """Ferme le bandeau de consentement Amazon s'il recouvre la page."""
    boutons = driver.find_elements(
        By.CSS_SELECTOR,
        "#sp-cc-accept, input[name='accept'], button[name='accept']",
    )
    for bouton in boutons:
        try:
            if bouton.is_displayed() and bouton.is_enabled():
                bouton.click()
                try:
                    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#sp-cc, .sp-cc")))
                except TimeoutException:
                    pass
                return
        except WebDriverException:
            continue


def analyser_page(driver, marketplace: str) -> List[Produit]:
    page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "captcha" in page_text or "robot check" in page_text or ("désolé" in page_text and "robot" in page_text):
        raise AccesRefuseError("Amazon a présenté une vérification anti-robot. Arrêt sans tentative de contournement.")

    results = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result'][data-asin]")
    for card in cards:
        asin = (card.get_attribute("data-asin") or "").strip()
        if not asin:
            continue
        title = _texte(card, "h2 a span") or _texte(card, "h2 span")
        if not title:
            continue
        normalized = " ".join(title.lower().split())
        if "asus v16" not in normalized:
            continue
        price = _premier_texte(card, SELECTEURS_PRIX)
        try:
            image_url = card.find_element(By.CSS_SELECTOR, "img.s-image").get_attribute("src")
        except WebDriverException:
            image_url = None
        rating = _premier_texte(card, SELECTEURS_NOTE)
        review_count = _premier_texte(card, SELECTEURS_AVIS)
        results.append(Produit(asin, title, price or None, rating, review_count, marketplace, image_url))
    return results


def rechercher(
    driver,
    domain: str,
    query: str,
    max_pages: int,
    wait_seconds: int,
    delay: float,
    max_products: int = 10,
) -> List[Produit]:
    search_url = "https://{}/s?k={}".format(domain, quote_plus(query))
    wait = WebDriverWait(driver, wait_seconds)
    unique = {}
    driver.get(search_url)
    _gerer_consentement(driver, wait)
    for page_number in range(1, max_pages + 1):
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        except TimeoutException:
            body = driver.find_element(By.TAG_NAME, "body").text.lower()
            if "captcha" in body or "robot check" in body:
                raise AccesRefuseError("Vérification Amazon détectée. Le scraper s'arrête.")
            break
        for produit in analyser_page(driver, domain):
            unique[produit.asin] = produit
            if len(unique) >= max_products:
                break
        if len(unique) >= max_products:
            break
        _gerer_consentement(driver, wait)
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.s-pagination-next:not(.s-pagination-disabled)")
        if not next_buttons or page_number == max_pages:
            break
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next:not(.s-pagination-disabled)")))
            next_buttons[0].click()
        except ElementClickInterceptedException:
            # Le bandeau peut apparaître après le chargement ou rester superposé.
            _gerer_consentement(driver, wait)
            try:
                wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#sp-cc, .sp-cc")))
            except TimeoutException:
                pass
            suivant = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next:not(.s-pagination-disabled)")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", suivant)
            suivant.click()
        time.sleep(delay)
    produits = list(unique.values())[:max_products]
    _completer_depuis_fiches(driver, produits, wait_seconds)
    return produits
