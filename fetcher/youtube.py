"""读 YouTube 公开页面：搜索页（找候选）和视频页（拿准确发布时间、时长）。不用 key，只用标准库。

代理：默认照系统的 HTTPS_PROXY 走（国内要靠代理才上得了 YouTube），设 LEADERS_NO_PROXY=1 强制直连。
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")


def opener(*handlers) -> urllib.request.OpenerDirector:
    if os.environ.get("LEADERS_NO_PROXY", "").lower() in ("1", "true", "yes"):
        return urllib.request.build_opener(urllib.request.ProxyHandler({}), *handlers)
    return urllib.request.build_opener(*handlers)


OPENER = opener()

# 搜索过滤（YouTube 的 sp 参数）：上传时间 + 时长 20 分钟以上。实测本周那档只回 20 分钟以上、本周的。
SP_WEEK = "EgQIAxgC"
SP_YEAR = "EgQIBRgC"

VID_RE = re.compile(r"[A-Za-z0-9_-]{11}")
UNIT_S = {"s": 1, "sec": 1, "second": 1, "m": 60, "min": 60, "minute": 60, "h": 3600, "hr": 3600, "hour": 3600,
          "d": 86400, "day": 86400, "w": 604800, "wk": 604800, "week": 604800, "mo": 2592000, "month": 2592000,
          "y": 31536000, "yr": 31536000, "year": 31536000}
AGO_RE = re.compile(r"(\d+)\s*(mo|months?|minutes?|mins?|m|seconds?|secs?|s|hours?|hrs?|h|days?|d|weeks?|wks?|w|years?|yrs?|y)\s+ago", re.I)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


class Blocked(Exception):
    """YouTube 限流或要人机验证：这一轮别再请求了。"""


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        html = OPENER.open(req, timeout=25).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise Blocked("429")
        raise
    if "confirm you" in html and "not a bot" in html:
        raise Blocked("人机验证")
    return html


def _var(html: str, name: str) -> dict:
    i = html.find(name + " = ")
    if i < 0:
        raise ValueError(f"页面里没有 {name}")
    d, _ = json.JSONDecoder().raw_decode(html, i + len(name) + 3)
    if not isinstance(d, dict):
        raise ValueError(f"{name} 不是对象")
    return d


def _text(node) -> str:
    if not isinstance(node, dict):
        return ""
    return node.get("simpleText") or "".join(r.get("text", "") for r in node.get("runs") or [] if isinstance(r, dict))


def _renderers(x):
    if isinstance(x, dict):
        if isinstance(x.get("videoRenderer"), dict):
            yield x["videoRenderer"]
        for v in x.values():
            yield from _renderers(v)
    elif isinstance(x, list):
        for v in x:
            yield from _renderers(v)


def _ago(text: str, ref: datetime) -> Optional[datetime]:
    m = AGO_RE.search(text or "")
    if not m:
        return None
    unit = m.group(2).lower()
    unit = unit if unit in UNIT_S else unit.rstrip("s")
    if unit not in UNIT_S:
        return None
    return ref - timedelta(seconds=int(m.group(1)) * UNIT_S[unit])


def _hms(text: str) -> int:
    parts = [int(p) for p in re.findall(r"\d+", text or "")]
    sec = 0
    for p in parts[-3:]:
        sec = sec * 60 + p
    return sec


def search(query: str, sp: str, ref: datetime) -> List[Dict]:
    """搜一次，返回列表里每条视频的标题、频道、大约发布时间、时长、摘要。"""
    q = urllib.parse.quote_plus(query)
    d = _var(_get(f"https://www.youtube.com/results?search_query={q}&sp={sp}"), "var ytInitialData")
    # 结果为空是正常的（这周没人上传），但结构认不出就当取数失败，不能说成「没有新视频」
    if not isinstance((d.get("contents") or {}).get("twoColumnSearchResultsRenderer"), dict):
        raise ValueError("搜索页结构变了（没有 twoColumnSearchResultsRenderer）")
    out = []
    for r in _renderers(d):
        vid = r.get("videoId")
        if not isinstance(vid, str) or not VID_RE.fullmatch(vid) or r.get("upcomingEventData"):
            continue
        pub = _ago(_text(r.get("publishedTimeText")), ref)
        dur = _hms(_text(r.get("lengthText")))
        if not pub or not dur:          # 正在直播的没有时间和时长，播完再收
            continue
        snip = " ".join(_text(s.get("snippetText")) for s in r.get("detailedMetadataSnippets") or [] if isinstance(s, dict))
        badges = [((b or {}).get("metadataBadgeRenderer") or {}).get("style", "") for b in r.get("ownerBadges") or []]
        owner = (r.get("ownerText") or {}).get("runs") or [{}]
        cid = (((owner[0] or {}).get("navigationEndpoint") or {}).get("browseEndpoint") or {}).get("browseId", "")
        views = re.sub(r"\D", "", _text(r.get("viewCountText")))
        out.append({
            "id": vid, "title": _text(r.get("title")), "channel": _text(r.get("ownerText")), "channelId": cid,
            "verified": any("VERIFIED" in b for b in badges), "duration": dur, "published": iso(pub), "exact": False,
            "views": int(views) if views else None, "snippet": (snip or _text(r.get("descriptionSnippet")))[:500],
        })
    return out


def fetch_page(vid: str) -> Dict:
    """打开视频页，拿准确的发布时间、时长、完整简介。"""
    pr = _var(_get(f"https://www.youtube.com/watch?v={vid}"), "ytInitialPlayerResponse")
    vd = pr.get("videoDetails") or {}
    if vd.get("videoId") and vd["videoId"] != vid:
        raise ValueError("页面给的是别的视频")
    mf = (pr.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    dates = [str(mf.get(k) or "") for k in ("publishDate", "uploadDate")]
    # 优先带时分的；两个都只有日期就记这一天，页面上照样标「约」
    raw = next((s for s in dates if "T" in s and parse_iso(s)), "") or next((s for s in dates if parse_iso(s)), "")
    pub = parse_iso(raw)
    if not pub:
        raise ValueError("拿不到发布时间")
    secs = str(vd.get("lengthSeconds") or "")
    if not secs.isdigit() or int(secs) <= 0:
        raise ValueError("拿不到时长")       # 按开页失败算，下轮再开，不当成短视频扔掉
    views = str(vd.get("viewCount") or "")
    return {
        "published": iso(pub), "timed": "T" in raw, "duration": int(secs),
        "desc": (vd.get("shortDescription") or "")[:1500], "title": vd.get("title") or "",
        "channel": vd.get("author") or "", "channelId": vd.get("channelId") or "",
        "upcoming": bool(vd.get("isUpcoming")), "views": int(views) if views.isdigit() else None,
    }
