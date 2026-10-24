from datetime import datetime
import csv
from pathlib import Path


def exporter_csv(produits, directory: Path) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / ("asus_v16_{}.csv".format(datetime.now().strftime("%Y%m%d_%H%M%S")))
    fields = ["asin", "titre", "prix", "note", "avis", "marketplace", "image_url"]
    with output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: product.to_dict().get(field) for field in fields} for product in produits)
    return output
