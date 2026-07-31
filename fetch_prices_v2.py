#!/usr/bin/env python3
import fetch_prices as monitor

# Active monitoring set. Newly added products use their price at the time of
# addition as the initial baseline.
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
    769: {"name": "PS5 真三国无双 起源", "baseline": 380},
    2361: {"name": "NS2 鼠探 私家侦探", "baseline": 198},
    814: {"name": "PS5 毁灭战士 暗黑时代", "baseline": 189},
}

if __name__ == "__main__":
    raise SystemExit(monitor.main())
