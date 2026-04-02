from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from prometheus_fastapi_instrumentator import Instrumentator
from pymongo.errors import DuplicateKeyError

from app.database import get_products_collection
from app.models import ProductCreate, ProductOut
from app.schemas import product_doc_to_dict
from app.utils import get_usd_to_eur_rate


# Simple inventory API for the Web Services assignment (FastAPI + MongoDB).
app = FastAPI(title="Inventory API")

# Wire up Prometheus metrics early (Starlette won't let you add middleware during startup).
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.on_event("startup")
def _startup() -> None:
    col = get_products_collection()
    # ProductID is our natural key, so enforce it.
    col.create_index("product_id", unique=True)
    col.create_index("name")


@app.get("/getSingleProduct", response_model=ProductOut)
def get_single_product(product_id: int = Query(..., ge=1)) -> dict[str, Any]:
    col = get_products_collection()
    doc = col.find_one({"product_id": product_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_doc_to_dict(doc)


@app.get("/getAll", response_model=list[ProductOut])
def get_all() -> list[dict[str, Any]]:
    col = get_products_collection()
    docs = col.find({}, {"_id": 0}).sort("product_id", 1)
    return list(docs)


@app.post("/addNew", response_model=ProductOut, status_code=201)
def add_new(product: ProductCreate) -> dict[str, Any]:
    col = get_products_collection()
    doc = product.model_dump()
    try:
        col.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="ProductID already exists")
    return doc


@app.delete("/deleteOne")
def delete_one(product_id: int = Query(..., ge=1)) -> dict[str, Any]:
    col = get_products_collection()
    result = col.delete_one({"product_id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": True, "product_id": product_id}


@app.get("/startsWith", response_model=list[ProductOut])
def starts_with(letter: str = Query(..., min_length=1, max_length=1)) -> list[dict[str, Any]]:
    col = get_products_collection()
    regex = f"^{letter}"
    docs = col.find({"name": {"$regex": regex, "$options": "i"}}, {"_id": 0}).sort("product_id", 1)
    return list(docs)


@app.get("/paginate", response_model=list[ProductOut])
def paginate(
    start_id: int = Query(..., ge=1),
    end_id: int = Query(..., ge=1),
) -> list[dict[str, Any]]:
    if end_id < start_id:
        raise HTTPException(status_code=400, detail="end_id must be >= start_id")

    col = get_products_collection()
    # The brief mentions a start/end ID *and* "batches of 10", so we do both.
    docs = (
        col.find({"product_id": {"$gte": start_id, "$lte": end_id}}, {"_id": 0})
        .sort("product_id", 1)
        .limit(10)
    )
    return list(docs)


@app.get("/convert")
async def convert(product_id: int = Query(..., ge=1)) -> dict[str, Any]:
    col = get_products_collection()
    doc = col.find_one({"product_id": product_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    rate = await get_usd_to_eur_rate()
    usd_price = float(doc["unit_price"])
    eur_price = round(usd_price * rate, 2)

    return {
        "product_id": int(doc["product_id"]),
        "name": str(doc["name"]),
        "unit_price_usd": usd_price,
        "unit_price_eur": eur_price,
        "usd_to_eur_rate": rate,
    }

