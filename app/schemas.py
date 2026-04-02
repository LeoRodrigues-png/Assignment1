from __future__ import annotations

from typing import Any


def product_doc_to_dict(doc: dict[str, Any]) -> dict[str, Any]:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc

