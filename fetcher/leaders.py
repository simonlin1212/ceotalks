#!/usr/bin/env python3
"""CEO Talks 抓取端：名单上这些人最近在 YouTube 上本人亲自讲的播客、访谈、演讲、座谈，按人排、新的在前。

只用 Python 3.9 自带的库。名单在 people.json；AI 判断那步可换可关（见 judge.py）；数据和页面的位置可以用环境变量改。

怎么取（每轮）：
1. 每人搜两次 YouTube（直接读搜索页）：引号里的全名，和全名加 interview；本周上传、20 分钟以上（--backfill 改成今年）。
   搜索页给的是「5 小时前」「2 周前」这种大约时间，先按它记。只搜名字时，马斯克这种前 20 条几乎全是别人的解说，
   加 interview 才搜得到本人出镜的。
2. 标题或摘要里有这个人的名字（或「英伟达 CEO」这类头衔）才算候选。
3. 一批交给 AI 判：是不是本人在讲，还是别人讲这个人、解说、剪辑、搬运；顺带给中文标题和一句话讲什么。判过的不重判。
4. 只给判下来要收的开视频页，拿准确的发布时间、时长（串行、隔 2 秒、一轮最多 30 个；碰到 429 或人机验证就停这一轮）。
   实测一口气开 60 多个视频页 YouTube 就要人机验证，所以不给每个候选都开。
   机房的机器（如 GitHub Actions）开视频页第一下就要人机验证，在那种地方跑设 LEADERS_MAX_PAGES=0 不开，
   页面上的时间就一直是大约的，AI 也只看得到搜索页的短摘要。
5. AI 没开或不通：people.json 里认的官方频道和访谈节目先照放（页面标「没判」），其余等 AI 判。

文件（都能用环境变量改）：
- LEADERS_DATA（默认 项目/data）：累积库 store.json（搜索只给最近的，历史靠它留着）、锁 .lock、AI 回乱码时的原话。
- LEADERS_OUT（默认 项目/site/data/leaders.json）：给页面读的数据。
- LEADERS_MAX_PAGES（默认 30）：一轮最多开几个视频页，0 = 不开。

跑法: python3 -I fetcher/leaders.py [--backfill] [--ai off|openai|command] [--only 人名键,...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)   # 用 -I 跑时脚本所在目录不在搜索路径里
import judge as J  # noqa: E402
import people as P  # noqa: E402
import youtube as Y  # noqa: E402
from file_lock import exclusive_file_lock  # noqa: E402

ROOT = os.path.dirname(HERE)
DATA = os.environ.get("LEADERS_DATA") or os.path.join(ROOT, "data")
OUT = os.environ.get("LEADERS_OUT") or os.path.join(ROOT, "site", "data", "leaders.json")
STORE = os.path.join(DATA, "store.json")
LOCK = os.path.join(DATA, ".lock")
AI_BAD = os.path.join(DATA, "ai_bad_last.txt")

GAP = 2.0              # 两次请求之间隔几秒（串行）
MAX_PAGES = int(os.environ.get("LEADERS_MAX_PAGES") or 30)   # 一轮最多打开多少个视频页，多的下一轮接着开；0 = 不开
PAGE_TRIES = 3         # 同一个视频页开三次都失败就不再开，按大约时间放
MIN_SEC = 20 * 60      # 正片门槛：20 分钟
KEEP_SHOW = 20         # 每人页面上放多少条
KEEP_DAYS = 400        # 库里留多久
AI_BATCH = 8
AI_TRIES = 3           # 同一条 AI 三次都没给答复，之后一天只再问一次
AI_RETRY_AFTER = timedelta(days=1)
AI_VERSION = J.AI_VERSION
QUERIES = ('"{}"', '"{}" interview')
RULE = "本人亲自讲的播客、访谈、演讲、座谈，20 分钟以上；别人讲他们的、剪辑、搬运、翻译配音不收"

PEOPLE, OFFICIAL_CO, INTERVIEW_ONLY = P.load()
PERSON = {p.key: p for p in PEOPLE}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


iso = Y.iso
parse_iso = Y.parse_iso


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%F %T')}] {msg}", flush=True)


def write_text_atomic(path: str, text: str) -> None:
    """先写临时文件再换名：中断不会留下半个文件。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".leaders-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_json_atomic(path: str, doc) -> None:
    write_text_atomic(path, json.dumps(doc, ensure_ascii=False, indent=1))


def _good_rec(rid, v) -> bool:
    """库里一条记录的必需字段齐不齐、类型对不对；不对的整条丢掉，别让一条坏的拖垮整轮。
    名单里已经删掉的人，记录留在库里不动（加回来还在），只是不判、不上页面。"""
    return (isinstance(rid, str) and isinstance(v, dict) and isinstance(v.get("id"), str)
            and bool(Y.VID_RE.fullmatch(v["id"])) and isinstance(v.get("person"), str)
            and rid == f"{v['person']}:{v['id']}"
            and isinstance(v.get("title"), str) and isinstance(v.get("channel"), str)
            and parse_iso(v.get("published")) is not None
            and isinstance(v.get("duration"), int) and not isinstance(v.get("duration"), bool))


def load_store() -> dict:
    try:
        with open(STORE, encoding="utf-8") as f:
            st = json.load(f)
        if isinstance(st, dict) and isinstance(st.get("videos"), dict):
            vids = st["videos"]
            bad = [rid for rid, v in vids.items() if not _good_rec(rid, v)]
            for rid in bad:
                del vids[rid]
            if bad:
                log(f"库里 {len(bad)} 条记录字段不对，丢掉了：{', '.join(map(str, bad[:5]))}")
            s = st.get("searched")
            st["searched"] = {k: t for k, t in s.items() if isinstance(k, str) and isinstance(t, str)} if isinstance(s, dict) else {}
            st["runs"] = [r for r in st.get("runs") or [] if isinstance(r, dict)] if isinstance(st.get("runs"), list) else []
            return st
        raise ValueError("顶层不是 {videos: {...}}")
    except FileNotFoundError:
        pass
    except (OSError, ValueError) as e:
        # 库坏了不覆盖：挪开留着，换个空库
        bad = STORE + ".bad-" + datetime.now().strftime("%Y%m%d%H%M%S")
        try:
            os.replace(STORE, bad)
        except OSError:
            pass
        log(f"库读不了（{e!r:.120}），已挪到 {os.path.basename(bad)}，按空库起")
    return {"videos": {}, "searched": {}, "runs": []}


def trusted(v: dict) -> bool:
    """AI 没判时能不能先放上页面。每次现算，频道信息后来补全了也跟着变。"""
    if v.get("channelId") in INTERVIEW_ONLY:
        return True
    return bool(v.get("verified") and (v.get("channel") or "").lower() in OFFICIAL_CO)


def shown(v: dict) -> bool:
    """上不上页面：AI 判过的看判的结果；没判过的只放认得的频道。"""
    if v.get("aiv") == AI_VERSION:
        return v.get("keep") is True
    return trusted(v)


# ---------- 主流程 ----------

def run(args) -> int:
    if getattr(args, "page_only", False):
        try:
            with exclusive_file_lock(LOCK, blocking=False):
                return _page_only()
        except BlockingIOError:
            log("另一轮还在跑，这次跳过")
            return 0
    keys = [k.strip() for k in args.only.split(",") if k.strip()] if args.only else [p.key for p in PEOPLE]
    unknown = [k for k in keys if k not in PERSON]
    if unknown:
        log(f"不认识的人名键：{unknown}；可用：{', '.join(PERSON)}")
        return 2
    try:
        provider = J.from_env(args.ai)
    except (ValueError, OSError) as e:
        log(f"AI 设置不对：{e}")
        return 2
    try:
        with exclusive_file_lock(LOCK, blocking=False):
            return _run(args, keys, provider)
    except BlockingIOError:
        log("另一轮还在跑，这次跳过")
        return 0


def _run(args, keys: List[str], provider: J.Provider) -> int:
    st = load_store()
    vids: Dict = st["videos"]
    start = now_utc()
    errors: List[str] = []
    blocked = False
    sp = Y.SP_YEAR if args.backfill else Y.SP_WEEK

    # 1) 搜索（每人两种搜法）
    cands: Dict[Tuple[str, str], Dict] = {}   # (人, 视频) → 列表里的信息
    reqs = 0
    for key in keys:
        if blocked:
            break
        p = PERSON[key]
        ok = False
        for query in QUERIES:
            if reqs:
                time.sleep(GAP)
            reqs += 1
            try:
                items = Y.search(query.format(p.en), sp, now_utc())
            except Y.Blocked as e:
                blocked = True
                errors.append(f"YouTube 限流（{e}），这轮停在搜 {p.zh}，后面的人下轮再搜")
                break
            except Exception as e:  # 一种搜法不通不拖累别的
                errors.append(f"搜 {p.zh}（{query.format('')[2:].strip() or '名字'}）失败：{str(e)[:120]}")
                continue
            ok = True
            for it in items:
                if it["duration"] >= MIN_SEC and (P.name_hits(p, it["title"], it["snippet"])
                                                  or P.name_hits(p, it["snippet"], it["title"], allow_role=False)):
                    cands.setdefault((key, it["id"]), it)
        if ok:
            st["searched"][key] = iso(now_utc())
    log(f"搜完 {sum(1 for k in keys if (st['searched'].get(k) or '') >= iso(start))}/{len(keys)} 人，候选 {len(cands)}")

    # 2) 新的进库（先按大约时间），老的更新播放量
    new = 0
    for (key, vid), it in cands.items():
        rec = vids.get(f"{key}:{vid}")
        if rec:
            if it.get("views") is not None:
                rec["views"] = it["views"]
            for k in ("channelId", "verified"):
                if it.get(k) and not rec.get(k):
                    rec[k] = it[k]
            continue
        if (parse_iso(it["published"]) or start) < start - timedelta(days=KEEP_DAYS):
            continue
        rec = {k: it.get(k) for k in ("id", "title", "channel", "channelId", "verified", "views", "snippet",
                                       "published", "duration", "exact")}
        rec.update(person=key, desc=it.get("desc", ""), firstSeen=iso(start))
        vids[f"{key}:{vid}"] = rec
        new += 1

    # 3) AI 判没判过的（新的在前）；一批不通再试下一批，连着两批不通就停。
    #    次数按判法版本记；三次没答复的之后一天再问一次
    def tries(v):
        return v.get("aiTries", 0) if v.get("aiTriesV") == AI_VERSION else 0

    def due(v):
        last = parse_iso(v.get("aiLast"))
        return tries(v) < AI_TRIES or not last or start - last >= AI_RETRY_AFTER

    def miss(v):
        v.update(aiTries=tries(v) + 1, aiTriesV=AI_VERSION, aiLast=iso(now_utc()))

    ai_ok = None
    pending = [v for v in vids.values() if v["person"] in PERSON and v.get("aiv") != AI_VERSION and due(v)]
    pending.sort(key=lambda v: v["published"], reverse=True)
    if pending and provider.name != "off":
        fails = ok_batches = bad_batches = missing = 0
        stopped = False
        for b in range(0, len(pending), AI_BATCH):
            batch = pending[b:b + AI_BATCH]
            context: Dict[str, List[Dict]] = {}
            for v in sorted(vids.values(), key=lambda v: v["published"], reverse=True):
                if v.get("keep") and v.get("aiv") == AI_VERSION:
                    context.setdefault(v["person"], []).append(v)
            res = J.judge(provider, batch, context, PERSON, AI_BAD, log)
            if not res:   # 没回，或者一条能用的都没有：都算这批不通
                for v in batch:
                    miss(v)
                fails += 1
                bad_batches += 1
                if fails >= 2:
                    stopped = True
                    errors.append("AI 连着两批不通，没判的下轮再判（官方频道和访谈节目先照放）")
                    break
                continue
            fails = 0
            ok_batches += 1
            for i, v in enumerate(batch):
                r = res.get(i)
                if r:
                    v.update(keep=r["keep"], kind=r["kind"], zh=r["zh"], gist=r["gist"], dup=r["dup"], aiv=AI_VERSION)
                    for k in ("aiTries", "aiTriesV", "aiLast"):
                        v.pop(k, None)
                else:
                    miss(v)
                    missing += 1
        ai_ok = ok_batches > 0 and not stopped
        if (bad_batches or missing) and not stopped:
            errors.append(f"AI 这轮有 {bad_batches} 批没回成、{missing} 条没给能用的答复，下轮再判")
        log(f"AI（{provider.name}）判完 {len(pending)} 条里的 {sum(1 for v in pending if v.get('aiv') == AI_VERSION)} 条")
    elif pending:
        log(f"AI 没开，{len(pending)} 条没判的先不上页面（认得的官方频道、访谈节目除外）")

    # 4) 要上页面、还只有大约时间的，开视频页拿准确时间（新的在前）
    pages = 0
    need = [v for v in vids.values() if v["person"] in PERSON and not v.get("exact")
            and v.get("pageTries", 0) < PAGE_TRIES and shown(v)]
    need.sort(key=lambda v: v["published"], reverse=True)
    done: Dict[str, Dict] = {}   # 同一个视频分属两个人时只开一次
    for v in need:
        if blocked or pages >= MAX_PAGES:
            break
        pg = done.get(v["id"])
        if pg is None:
            if pages:
                time.sleep(GAP)
            pages += 1
            try:
                pg = done[v["id"]] = Y.fetch_page(v["id"])
            except Y.Blocked as e:
                blocked = True
                errors.append(f"YouTube 限流（{e}），这轮停开视频页，没开的先按大约时间放")
                break
            except Exception as e:
                v["pageTries"] = v.get("pageTries", 0) + 1
                errors.append(f"开 {v['id']} 失败：{str(e)[:100]}")
                continue
        if pg["upcoming"]:               # 还没开播的：等播完再来
            v["pageTries"] = v.get("pageTries", 0) + 1
            continue
        if pg["duration"] < MIN_SEC:
            v.update(keep=False, aiv=AI_VERSION, kind=v.get("kind") or "其他")
            continue
        v.update(published=pg["published"], duration=pg["duration"], exact=True,
                 desc=pg["desc"] or v.get("desc", ""), channel=pg["channel"] or v["channel"],
                 channelId=pg["channelId"] or v.get("channelId", ""),
                 views=pg["views"] if pg["views"] is not None else v.get("views"))
        if pg["timed"]:
            v.pop("dayOnly", None)
        else:
            v["dayOnly"] = True
    left = sum(1 for v in need if not v.get("exact"))

    # 5) 清旧的、写库、出页面数据
    cutoff = start - timedelta(days=KEEP_DAYS)
    for rid in [rid for rid, v in vids.items() if (parse_iso(v.get("published")) or start) < cutoff]:
        del vids[rid]
    st["runs"] = (st.get("runs") or [])[-49:] + [{"at": iso(start), "mode": "backfill" if args.backfill else "week",
                                                   "people": len(keys), "cands": len(cands), "new": new, "pages": pages,
                                                   "pagesLeft": left, "ai": ai_ok, "aiProvider": provider.name,
                                                   "errors": errors[:10]}]
    doc = build_doc(vids, st["searched"], errors, ai_ok, provider.name, start)
    write_json_atomic(STORE, st)
    write_json_atomic(OUT, doc)
    n_shown = sum(len(p["videos"]) for p in doc["people"])
    log(f"候选 {len(cands)}（新进库 {new}），库里 {len(vids)}，页面上 {n_shown} 条；开视频页 {pages}，还差 {left} 条只有大约时间；"
        f"AI {'通' if ai_ok else ('没调' if ai_ok is None else '不通')}；问题 {len(errors)} 条")
    for e in errors:
        log("  " + e)
    return 0


def _page_only() -> int:
    """不搜、不叫 AI，只用库里现有的重出页面数据；更新时间、问题照最近一轮写，不假装刚抓过。"""
    st = load_store()
    last = (st.get("runs") or [{}])[-1]
    built = parse_iso(last.get("at")) or now_utc()
    doc = build_doc(st["videos"], st.get("searched") or {}, list(last.get("errors") or []), last.get("ai"),
                    str(last.get("aiProvider") or "off"), built)
    write_json_atomic(OUT, doc)
    log(f"只重出页面数据：页面上 {sum(len(p['videos']) for p in doc['people'])} 条，数据还是 {iso(built)} 那一轮的")
    return 0


def build_doc(vids: dict, searched: dict, errors: List[str], ai_ok, ai_name: str, start: datetime) -> dict:
    people = []
    for p in PEOPLE:
        mine = [v for v in vids.values() if v["person"] == p.key and shown(v)]
        mine.sort(key=lambda v: v["published"], reverse=True)
        people.append({
            "key": p.key, "zh": p.zh, "en": p.en, "role": p.role, "role_en": p.role_en, "searched": searched.get(p.key),
            "videos": [{
                "id": v["id"], "url": f"https://www.youtube.com/watch?v={v['id']}",
                "title": v["title"], "zh": v.get("zh") or "", "gist": v.get("gist") or "",
                "kind": v.get("kind") or "", "channel": v["channel"], "published": v["published"],
                "approx": not v.get("exact") or bool(v.get("dayOnly")), "duration": v["duration"], "views": v.get("views"),
                "judged": v.get("aiv") == AI_VERSION,
            } for v in mine[:KEEP_SHOW]],
        })
    return {"meta": {"built": iso(start), "ai": ai_ok, "aiProvider": ai_name, "errors": errors[:10], "rule": RULE},
            "people": people}


def main() -> int:
    ap = argparse.ArgumentParser(description="顶级人物播客（YouTube）")
    ap.add_argument("--backfill", action="store_true", help="搜今年的（第一次填库用），平时只搜本周")
    ap.add_argument("--ai", choices=["off", "openai", "command"], help="这一轮用哪种 AI，不写就看环境变量 LEADERS_AI")
    ap.add_argument("--only", default="", help="只跑这几个人，键用逗号隔开，如 jensen,lisasu")
    ap.add_argument("--page-only", action="store_true", help="不搜、不叫 AI，只用库里现有的重出页面数据（改了 people.json 的名字、头衔后用）")
    return run(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main())
