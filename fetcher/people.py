"""名单和认名字：从 people.json 读要追的人，判断一段标题或摘要里说的是不是这个人。

名单放在 people.json 里，加人删人不用改代码。
"""
from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional, Set, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
PEOPLE_FILE = os.environ.get("LEADERS_PEOPLE") or os.path.join(HERE, "people.json")


class Person:
    def __init__(self, d: dict):
        self.key = str(d["key"])
        self.zh = str(d["zh"])
        self.en = str(d["en"])
        self.role = str(d.get("role") or "")
        self.role_en = str(d.get("role_en") or "")
        self.names = [str(x) for x in d.get("names") or []]
        self.titles = [str(x) for x in d.get("titles") or []]
        self.short = str(d.get("short") or "").lower()
        self.short_ctx = str(d.get("short_ctx") or "")
        self.same_surname = str(d.get("same_surname") or "")
        if not re.fullmatch(r"[a-z0-9_]{1,32}", self.key):
            raise ValueError(f"人名键只能用小写字母、数字、下划线：{self.key!r}")
        if self.short and not self.short_ctx:
            raise ValueError(f"{self.key}：写了 short 就要写 short_ctx")
        self.full_p = _pat([w for w in self.names if w.lower() != self.short])   # 全名、姓
        self.short_p = _pat([self.short]) if self.short else None                  # 只有名
        self.role_p = _pat(self.titles, possessive=True)                           # 头衔


def _pat(words: List[str], possessive: bool = False) -> Optional[re.Pattern]:
    """几种写法合成一个正则：空格、连字符可有可无（Fei-Fei Li / Fei Fei Li / FeiFei Li）；头衔允许「Nvidia's CEO」。"""
    if not words:
        return None
    sep = r"(?:['’]s)?[\s\-]+" if possessive else r"[\s\-]?"
    alts = [sep.join(re.escape(part) for part in re.split(r"[\s\-]+", w) if part) for w in words]
    return re.compile(r"(?<![A-Za-z])(?:" + "|".join(alts) + r")(?![A-Za-z])", re.I)


def load(path: str = PEOPLE_FILE) -> Tuple[List[Person], Set[str], Dict[str, str]]:
    """返回 (名单, 认的公司官方频道名, 认的访谈节目频道编号→名字)。"""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    people = [Person(p) for p in d["people"]]
    keys = [p.key for p in people]
    if len(set(keys)) != len(keys):
        raise ValueError("people.json 里有重复的人名键")
    official = {str(x).lower() for x in d.get("official_channels") or []}
    interview = {str(k): str(v) for k, v in (d.get("interview_channels") or {}).items()}
    return people, official, interview


DASHES = re.compile(r"[­‐-―−﹘﹣－]")


def _norm(s: str) -> str:
    """各种连字符（Fei‑Fei 里的不断行连字符等）统一成 -，连着的空白并成一个。"""
    return re.sub(r"\s+", " ", DASHES.sub("-", s or ""))


def name_hits(p: Person, text: str, ctx: str = "", allow_role: bool = True) -> bool:
    """这段字里认得出这个人吗。allow_role=False 时只认名字。"""
    t = _norm(text)
    ctx = _norm(ctx)
    low = t.lower()
    if p.full_p and p.full_p.search(t):
        if p.same_surname and re.search(p.same_surname, low) and not re.search(re.escape(p.en.split()[0].lower()), low):
            return False
        return True
    if p.short_p and p.short_p.search(t):
        return bool(re.search(p.short_ctx, (t + " " + (ctx or "")[:500]).lower()))
    return bool(allow_role and p.role_p and p.role_p.search(t))
