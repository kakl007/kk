#!/usr/bin/env python3
import json
from pathlib import Path

from fetch_prices import API, extract_products, fetch_text, parse_id

KEYWORDS = {
    "真三国无双起源 PS5": ["真三国无双", "起源"],
    "鼠探 NS2": ["鼠探"],
    "毁灭战士暗黑时代 PS5": ["毁灭战士", "暗黑时代"],
}


def fetch_catalog() -> dict[int, dict]:
    all_by_id: dict[int, dict] = {}
    for page in range(1, 51):
        payload = json.loads(fetch_text(API.format(page=page)))
        products = extract_products(payload)
        if not products:
            break
        new_count = 0
        for product in products:
            pid = parse_id(product.get("id"))
            if pid is not None and pid not in all_by_id:
                all_by_id[pid] = product
                new_count += 1
        if new_count == 0:
            break
    return all_by_id


def main() -> None:
    catalog = fetch_catalog()
    results = {}
    for label, terms in KEYWORDS.items():
        matches = []
        for pid, product in catalog.items():
            name = str(product.get("store_name") or "")
            if all(term.lower() in name.lower() for term in terms):
                matches.append({
                    "id": pid,
                    "store_name": name,
                    "price": product.get("price"),
                    "cate_id": product.get("cate_id"),
                })
        results[label] = sorted(matches, key=lambda x: x["id"])

    output = {"catalog_count": len(catalog), "matches": results}
    path = Path("data/discovery.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
