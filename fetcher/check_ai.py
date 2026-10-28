#!/usr/bin/env python3
"""换 AI 之前先对一下：从库里挑判过的视频（收、不收各一半，新的在前），让现在设的 AI 重判一遍，看跟库里的判法一不一样。
只读库，不改库。AI 怎么设见 judge.py（LEADERS_AI 等环境变量）。

跑法: python3 -I fetcher/check_ai.py [--n 16] [--ai openai|command]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge as J  # noqa: E402
import leaders as L  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="拿库里判过的视频对一下现在设的 AI")
    ap.add_argument("--n", type=int, default=16, help="对几条（收、不收各一半）")
    ap.add_argument("--ai", choices=["openai", "command"], help="不写就看环境变量 LEADERS_AI")
    args = ap.parse_args()
    provider = J.from_env(args.ai)
    if provider.name == "off":
        L.log("AI 没开，没什么可对的（设 LEADERS_AI 或 --ai）")
        return 2
    with open(L.STORE, encoding="utf-8") as f:
        vids = json.load(f)["videos"]
    judged = sorted((v for v in vids.values() if v.get("aiv") == J.AI_VERSION and v.get("person") in L.PERSON
                     and not v.get("dup")), key=lambda v: v["published"], reverse=True)
    half = max(1, args.n // 2)
    sample = [v for v in judged if v.get("keep")][:half] + [v for v in judged if not v.get("keep")][:half]
    same = diff = none = 0
    rows = []
    for b in range(0, len(sample), L.AI_BATCH):
        batch = [dict(v) for v in sample[b:b + L.AI_BATCH]]
        res = J.judge(provider, batch, {}, L.PERSON, os.path.join(L.DATA, "ai_bad_check.txt"), L.log)
        for i, v in enumerate(batch):
            r = (res or {}).get(i)
            if r is None:
                none += 1
                mark = "没回"
            elif r["keep"] == bool(v.get("keep")):
                same += 1
                mark = "一样"
            else:
                diff += 1
                mark = "不一样"
            rows.append(f"{mark:4} 库里{'收' if v.get('keep') else '不收'} → 这次{'—' if r is None else ('收' if r['keep'] else '不收')}"
                        f"  {L.PERSON[v['person']].zh}  {v['title'][:70]}")
    for line in rows:
        print(line)
    L.log(f"对了 {len(sample)} 条：一样 {same}，不一样 {diff}，没回 {none}（AI：{provider.name}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
