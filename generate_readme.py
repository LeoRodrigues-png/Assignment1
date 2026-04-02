from __future__ import annotations

from datetime import datetime
from pathlib import Path


README_TXT = """Inventory API (FastAPI + MongoDB)
Generated: {generated_at}

FastAPI docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Endpoints:
1) GET /getSingleProduct?product_id=1001
   - product_id: int

2) GET /getAll

3) POST /addNew
   JSON body fields (Pydantic validated):
   - product_id: int
   - name: str
   - unit_price: float
   - stock_quantity: int
   - description: str

4) DELETE /deleteOne?product_id=1001
   - product_id: int

5) GET /startsWith?letter=S
   - letter: str (single character)

6) GET /paginate?start_id=1001&end_id=1010
   - start_id: int
   - end_id: int
   Returns products in range, limited to 10 per call.

7) GET /convert?product_id=1001
   - product_id: int
   Calls external exchange-rate API and returns price in EUR.

Monitoring:
- GET /metrics (Prometheus format)

References:
- FastAPI documentation: https://fastapi.tiangolo.com/
"""


def main() -> None:
    root = Path(__file__).resolve().parent
    out_path = root / "README.txt"
    out_path.write_text(
        README_TXT.format(generated_at=datetime.now().isoformat(timespec="seconds")),
        encoding="utf-8",
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

