from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Produit:
    asin: str
    titre: str
    prix: Optional[str]
    note: Optional[str]
    avis: Optional[str]
    marketplace: str
    image_url: Optional[str] = None

    def to_dict(self):
        return asdict(self)
