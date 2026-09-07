#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import requests

HOST = "hailuo.dwzjd.com"
API = "https://hailuo.dwzjd.com/api/products?limit=300&page={page}"
TARGETS = {
    743: {"name": "PS5 GT赛车7", "baseline": 246},
    745: {"name": "PS5 星刃/剑星", "baseline": 185},
    737: {"name": "PS5 死亡搁浅2", "baseline": 234},
    789: {"name": "PS5 巫师3年度版", "baseline": 145},
    2416: {"name": "PS5 幻裂奇境", "baseline": 166},
    2183: {"name": "PS5 红色沙漠", "baseline": 454},
    2232: {"name": "PS5 卡普空大作9/安魂曲", "baseline": 305},
    889: {"name": "PS5 忍龙4", "baseline": 240},
    804: {"name": "PS5 阿凡达", "baseline": 110},
    778: {"name": "PS5 龙之信条2", "baseline": 138},
    753: {"name": "PS5 刺客信条 影", "baseline": 199},
    2297: {"name": "NS2 马里奥兄弟惊奇", "baseline": 297},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://hailuo.dwzjd.com/",
}
DATA_DIR = Path("data")
LATEST = DATA_DIR / "latest.json"
LAST_GOOD = DATA_DIR / "last_good.json"
HISTORY = DATA_DIR / "history.json"


def now_cn() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


def json_dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def resolve_ips(host: str) -> list[str]:
    ips: list[str] = []
    try:
        for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM):
            ip = item[4][0]
            if ":" not in ip and ip not in ips:
                ips.append(ip)
    except Exception:
        pass

    doh_endpoints = [
        ("https://dns.alidns.com/resolve", {}),
        ("https://1.1.1.1/dns-query", {"Accept": "application/dns-json"}),
        ("https://dns.google/resolve", {}),
    ]
    for endpoint, headers in doh_endpoints:
        try:
            r = requests.get(endpoint, params={"name": host, "type": "A"}, headers=headers, timeout=12)
            r.raise_for_status()
            payload = r.json()
            for answer in payload.get("Answer", []) or []:
                if int(answer.get("type", 0)) == 1:
                    ip = str(answer.get("data", "")).strip()
                    if ip and ip not in ips:
                        ips.append(ip)
        except Exception:
            continue
    return ips


def fetch_text(url: str) -> str:
    errors: list[str] = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.raise_for_status()
        return r.text
    except Exception as e:
        errors.append(f"direct={type(e).__name__}:{e}")

    for ip in resolve_ips(HOST):
        cmd = [
            "curl", "-fsSL", "--connect-timeout", "12", "--max-time", "30",
            "--retry", "2", "--retry-delay", "1",
            "--resolve", f"{HOST}:443:{ip}",
            "-H", f"User-Agent: {HEADERS['User-Agent']}",
            "-H", f"Accept: {HEADERS['Accept']}",
            "-H", f"Referer: {HEADERS['Referer']}",
            url,
        ]
        try:
            p = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if p.stdout.strip():
                return p.stdout
        except Exception as e:
            errors.append(f"resolve({ip})={type(e).__name__}:{e}")
    raise RuntimeError(" | ".join(errors))


def candidate_lists(obj: Any) -> list[list[dict]]:
    found: list[list[dict]] = []
    if isinstance(obj, list):
        dicts = [x for x in obj if isinstance(x, dict)]
        if dicts:
            found.append(dicts)
        for x in obj:
            found.extend(candidate_lists(x))
    elif isinstance(obj, dict):
        for v in obj.values():
            found.extend(candidate_lists(v))
    return found


def extract_products(payload: Any) -> list[dict]:
    lists = candidate_lists(payload)
    if not lists:
        return []
    scored = []
    for lst in lists:
        score = sum(1 for x in lst if "id" in x) * 10 + sum(1 for x in lst if "price" in x) + sum(1 for x in lst if "store_name" in x)
        scored.append((score, len(lst), lst))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return scored[0][2] if scored and scored[0][0] > 0 else []


def parse_id(v: Any) -> int | None:
    try:
        return int(str(v).strip())
    except Exception:
        return None


def parse_price(v: Any) -> float | None:
    try:
        if isinstance(v, str):
            v = v.replace("¥", "").replace(",", "").strip()
        return float(v)
    except Exception:
        return None


def fetch_all() -> tuple[dict[int, dict], dict]:
    all_by_id: dict[int, dict] = {}
    page_meta = []
    for page in range(1, 51):
        url = API.format(page=page)
        text = fetch_text(url)
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"page {page} returned non-JSON: {text[:300]!r}") from e
        products = extract_products(payload)
        page_meta.append({"page": page, "count": len(products)})
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
        # Do not stop just because the API returned fewer than the requested 300.
        # Hailuo currently returns ~100 items/page even with limit=300, so stopping
        # once existing targets are found can miss newly listed products on later pages.
    return all_by_id, {"pages": page_meta, "total_unique_ids": len(all_by_id)}


def update_history(items: list[dict], fetched_at: str) -> dict:
    history = load_json(HISTORY, {})
    date = fetched_at[:10]
    for item in items:
        key = str(item["id"])
        records = history.setdefault(key, [])
        rec = {"date": date, "fetched_at": fetched_at, "price": item["price"]}
        if records and records[-1].get("date") == date:
            records[-1] = rec
        else:
            records.append(rec)
        history[key] = records[-730:]
    json_dump(HISTORY, history)
    return history


def known_low(history: dict, pid: int) -> float | None:
    vals = []
    for rec in history.get(str(pid), []):
        p = parse_price(rec.get("price"))
        if p is not None:
            vals.append(p)
    return min(vals) if vals else None


def main() -> int:
    ts = now_cn()
    fetched_at = ts.isoformat(timespec="seconds")
    base = {
        "fetched_at": fetched_at,
        "timezone": "Asia/Shanghai",
        "source": API.replace("{page}", "N"),
        "target_ids": sorted(TARGETS),
    }
    try:
        all_by_id, meta = fetch_all()
        items = []
        missing = []
        for pid, cfg in TARGETS.items():
            raw = all_by_id.get(pid)
            if raw is None:
                missing.append(pid)
                continue
            price = parse_price(raw.get("price"))
            if price is None:
                missing.append(pid)
                continue
            items.append({
                "id": pid,
                "target_name": cfg["name"],
                "store_name": raw.get("store_name"),
                "price": price,
                "baseline": cfg["baseline"],
                "cate_id": raw.get("cate_id"),
                "raw": {k: raw.get(k) for k in ("id", "store_name", "price", "cate_id")},
            })
        if not items:
            raise RuntimeError(f"API parsed but none of the target IDs were found; meta={meta}")

        history = update_history(items, fetched_at)
        for item in items:
            item["known_low"] = known_low(history, item["id"])
            item["cumulative_change"] = round(float(item["baseline"]) - float(item["price"]), 2)

        result = {
            **base,
            "status": "ok" if not missing else "partial",
            "items": sorted(items, key=lambda x: x["id"]),
            "missing_ids": missing,
            "fetch_meta": meta,
        }
        json_dump(LATEST, result)
        json_dump(LAST_GOOD, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as e:
        error = {**base, "status": "error", "error": f"{type(e).__name__}: {e}"}
        json_dump(LATEST, error)
        print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
