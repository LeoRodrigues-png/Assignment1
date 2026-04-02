from __future__ import annotations

import csv
import os
from pathlib import Path

from dotenv import load_dotenv

from app.database import get_products_collection


def _parse_row(row: dict[str, str]) -> dict:
    return {
        "product_id": int(row["ProductID"]),
        "name": str(row["Name"]).strip(),
        "unit_price": float(row["UnitPrice"]),
        "stock_quantity": int(row["StockQuantity"]),
        "description": str(row["Description"]).strip(),
    }


def import_csv(csv_path: Path) -> tuple[int, int]:
    col = get_products_collection()

    inserted_or_updated = 0
    failed = 0

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"ProductID", "Name", "UnitPrice", "StockQuantity", "Description"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV headers must include: {sorted(required)}")

        for row in reader:
            try:
                doc = _parse_row(row)
                # Upsert means you can re-run imports without creating duplicates.
                col.update_one({"product_id": doc["product_id"]}, {"$set": doc}, upsert=True)
                inserted_or_updated += 1
            except Exception:
                failed += 1

    return inserted_or_updated, failed


def main() -> None:
    load_dotenv()

    default_csv = Path(__file__).resolve().parents[1] / "products.csv"
    csv_path = Path(os.getenv("PRODUCTS_CSV", str(default_csv))).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    ok, failed = import_csv(csv_path)
    print(f"Imported (upserted) {ok} products. Failed rows: {failed}")


if __name__ == "__main__":
    main()

