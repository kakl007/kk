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
    2453: {"name": "NS2 艾尔登法环 褪色者版", "baseline": 453},
    2457: {"name": "PS5 鬼武者 剑之道", "baseline": 245},
    2543: {"name": "PS5 致命躯壳2", "baseline": 279},
    2464: {"name": "NS2 火焰纹章 万紫千红", "baseline": 380},
    2454: {"name": "PS5 漫威金刚狼", "baseline": 229},
    2542: {"name": "NS2 最终幻想 共鸣（订购）", "baseline": 299},
    2603: {"name": "NS2 龙之信条2（订购）", "baseline": 279},
}

if __name__ == "__main__":
    raise SystemExit(monitor.main())
