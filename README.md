# Amazon Asus V16 - Selenium

Projet organisé en contrôleur, modèles, scraper et vues. Selenium collecte les résultats visibles pour Asus V16. Le scraper enregistre le prix, la note, le nombre d’avis, l’ASIN et l’URL de l’image Amazon. Il ne collecte ni n’exporte les URL des fiches produit. Les produits sont exportés en CSV.

## Installation et lancement

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

SQLite est inclus dans Python via `sqlite3`. La base `data/products.sqlite3` est créée ou mise à jour automatiquement, y compris les anciennes bases. À chaque scraping réussi, elle est remplacée par les résultats de ce lancement (10 produits maximum).

## Configuration

Modifie `config.py` pour choisir le marketplace (`www.amazon.fr`, `www.amazon.com`, `www.amazon.ca`…), la recherche, le nombre maximal de pages, le délai entre les pages et le mode headless. Chrome reste ouvert jusqu’à ce que tu appuies sur Entrée dans le terminal.

## Où trouver les données

- Base : `data/products.sqlite3`
- Export : fichiers CSV horodatés dans `exports/`

L’URL de l’image est enregistrée dans la base et le CSV. Utilise le scraper uniquement si tu es autorisé à collecter ces données et respecte les conditions applicables d’Amazon.
