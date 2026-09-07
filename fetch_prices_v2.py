#!/usr/bin/env python3
import fetch_prices as monitor

# Active monitoring set. Removed products are not fetched or written to new history.
monitor.TARGETS = {
    743: {"name": "PS5 GT赛车7", "baseline": 246},
    745: {"name": "PS5 星刃/剑星", "baseline": 185},
    737: {"name": "PS5 死亡搁浅2", "baseline": 234},
    789: {"name": "PS5 巫师3年度版", "baseline": 145},
    2416: {"name": "PS5 幻裂奇境", "baseline": 166},
    2183: {"name": "PS5 红色沙漠", "baseline": 454},
    2232: {"name": "PS5 卡普空大作9/安魂曲", "baseline": 305},
    889: {"name": "PS5 忍龙4", "baseline": 240},
    778: {"name": "PS5 龙之信条2", "baseline": 138},
    814: {"name": "PS5 毁灭战士 暗黑时代", "baseline": 189},
}

# One-time-safe dynamic discovery for the newly released NS2 Elden Ring Tarnished Edition.
# The first observed Hailuo price becomes its baseline; after discovery we hard-code
# the exact product ID/baseline so future cumulative changes remain stable.
all_by_id, _ = monitor.fetch_all()
eldens = []
for pid, raw in all_by_id.items():
    name = str(raw.get("store_name", ""))
    cate = str(raw.get("cate_id", ""))
    if cate == "41" and ("艾尔登法环" in name or "艾爾登法環" in name or "ELDEN RING" in name.upper()):
        price = monitor.parse_price(raw.get("price"))
        if price is not None:
            eldens.append((pid, name, price))

if len(eldens) == 1:
    pid, store_name, price = eldens[0]
    monitor.TARGETS[pid] = {"name": "NS2 艾尔登法环 褪色者版", "baseline": price}
elif len(eldens) > 1:
    raise RuntimeError(f"Multiple NS2 Elden Ring candidates found: {eldens}")
else:
    raise RuntimeError("NS2 Elden Ring Tarnished Edition not found in current Hailuo catalog")

if __name__ == "__main__":
    raise SystemExit(monitor.main())
