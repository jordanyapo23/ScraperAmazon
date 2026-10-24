import sqlite3
from pathlib import Path
from typing import Iterable, List

from app.models.produit import Produit


class Depot:
    """Stockage local SQLite, avec l'ASIN comme référence unique du produit."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    asin TEXT PRIMARY KEY, titre TEXT NOT NULL, prix TEXT,
                    note TEXT, avis TEXT, url TEXT NOT NULL, marketplace TEXT NOT NULL,
                    image_url TEXT
                )
            """)
            # Migration transparente des bases créées par les versions précédentes.
            columns = {row[1] for row in connection.execute("PRAGMA table_info(produits)")}
            if "image_url" not in columns:
                connection.execute("ALTER TABLE produits ADD COLUMN image_url TEXT")

    def _connect(self):
        return sqlite3.connect(str(self.database_path))

    def enregistrer(self, produits: Iterable[Produit]) -> int:
        rows = [(
            p.asin, p.titre, p.prix, p.note, p.avis, "",
            p.marketplace, p.image_url
        ) for p in produits]
        with self._connect() as connection:
            connection.executemany("""
                INSERT INTO produits (asin, titre, prix, note, avis, url, marketplace, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asin) DO UPDATE SET
                    titre=excluded.titre, prix=excluded.prix, note=excluded.note,
                    avis=excluded.avis, url=excluded.url, marketplace=excluded.marketplace,
                    image_url=excluded.image_url
            """, rows)
        return len(rows)

    def remplacer(self, produits: Iterable[Produit]) -> int:
        """Remplace atomiquement les anciens résultats par ceux du dernier scraping."""
        rows = [(
            p.asin, p.titre, p.prix, p.note, p.avis, "",
            p.marketplace, p.image_url
        ) for p in produits]
        with self._connect() as connection:
            connection.execute("DELETE FROM produits")
            connection.executemany("""
                INSERT INTO produits (asin, titre, prix, note, avis, url, marketplace, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
        return len(rows)

    def tous(self) -> List[Produit]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT asin, titre, prix, note, avis, marketplace, image_url "
                "FROM produits ORDER BY titre"
            ).fetchall()
        return [Produit(*row) for row in rows]
