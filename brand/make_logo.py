#!/usr/bin/env python3
"""CEO Talks 标志：橙色对话气泡里三根声音条；字标 CEO 粗、TALKS 细，都用线条画，不靠字体，哪儿打开都一样。
跑一次写出 site/brand/ 下的 mark.svg、logo.svg（深底用）、logo-light.svg（浅底用）和 site/favicon.svg。

    python3 -I brand/make_logo.py
"""
import math
import pathlib

SITE = pathlib.Path(__file__).resolve().parent.parent / "site"
ORANGE, CREAM, DARK = "#ff5a1f", "#f3eee6", "#0c0b0a"


def n(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


# ---------- 图形：气泡 + 声音条（48×48） ----------

BUBBLE = "M13 2H35A11 11 0 0 1 46 13V27A11 11 0 0 1 35 38H24L12 46.5L13.5 38H13A11 11 0 0 1 2 27V13A11 11 0 0 1 13 2Z"
BARS = [(15, 10), (24, 19), (33, 12)]   # (x, 高)，以 y=20 为中线


def mark(x=0.0, y=0.0, s=1.0):
    bars = "".join(f"M{n(bx)} {n(20 - h / 2)}V{n(20 + h / 2)}" for bx, h in BARS)
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(s)})">'
            f'<path fill="{ORANGE}" d="{BUBBLE}"/>'
            f'<path fill="none" stroke="{DARK}" stroke-width="5.5" stroke-linecap="round" d="{bars}"/></g>')


# ---------- 字标：每个字母给中线路径和宽度（x 起点，top 顶，h 高） ----------

def C(x, top, h):
    r = h / 2; cx = x + r; cy = top + r; a = math.radians(46)
    x1 = cx + r * math.cos(a)
    return f"M{n(x1)} {n(cy - r * math.sin(a))}A{n(r)} {n(r)} 0 1 0 {n(x1)} {n(cy + r * math.sin(a))}", x1 - x


def E(x, top, h):
    w = 0.6 * h
    return f"M{n(x + w)} {n(top)}H{n(x)}V{n(top + h)}H{n(x + w)}M{n(x)} {n(top + h / 2)}H{n(x + 0.84 * w)}", w


def O(x, top, h):
    r = h / 2
    return f"M{n(x)} {n(top + r)}a{n(r)} {n(r)} 0 1 0 {n(h)} 0a{n(r)} {n(r)} 0 1 0 {n(-h)} 0", h


def T(x, top, h):
    w = 0.74 * h
    return f"M{n(x)} {n(top)}H{n(x + w)}M{n(x + w / 2)} {n(top)}V{n(top + h)}", w


def A(x, top, h):
    w = 0.86 * h; t = 0.64
    return (f"M{n(x)} {n(top + h)}L{n(x + w / 2)} {n(top)}L{n(x + w)} {n(top + h)}"
            f"M{n(x + w / 2 * (1 - t))} {n(top + t * h)}H{n(x + w / 2 * (1 + t))}"), w


def L(x, top, h):
    w = 0.54 * h
    return f"M{n(x)} {n(top)}V{n(top + h)}H{n(x + w)}", w


def K(x, top, h):
    w = 0.64 * h
    return (f"M{n(x)} {n(top)}V{n(top + h)}M{n(x + w)} {n(top)}L{n(x)} {n(top + 0.62 * h)}"
            f"M{n(x + 0.36 * w)} {n(top + 0.39 * h)}L{n(x + 1.02 * w)} {n(top + h)}"), 1.02 * w


def S(x, top, h):
    w = 0.66 * h; rx = w / 2; ry = h / 4; c = x + rx; a = math.radians(28)
    y1 = top + ry; y2 = top + 3 * ry
    return (f"M{n(c + rx * math.cos(a))} {n(y1 - ry * math.sin(a))}"
            f"A{n(rx)} {n(ry)} 0 1 0 {n(c)} {n(top + 2 * ry)}"
            f"A{n(rx)} {n(ry)} 0 1 1 {n(c - rx * math.cos(a))} {n(y2 + ry * math.sin(a))}"), w


def word(letters, x, cap_top, cap_h, sw, gap):
    """一串字母，cap_top / cap_h 是看得见的顶和高；中线往里收半个线宽。返回 (path, 结束的 x)。"""
    top, h = cap_top + sw / 2, cap_h - sw
    x += sw / 2
    parts = []
    for i, (fn, kern) in enumerate(letters):
        if i:
            x += gap + kern
        d, w = fn(x, top, h)
        parts.append(d)
        x += w
    return "".join(parts), x + sw / 2


CAP_TOP, CAP_H = 9.0, 24.0
HEAVY, LIGHT = 5.4, 2.9


def wordmark(x, ink):
    ceo, x = word([(C, 0), (E, 0), (O, -0.6)], x, CAP_TOP, CAP_H, HEAVY, 4.2 + HEAVY)
    talks, x = word([(T, 0), (A, -6.2), (L, 0), (K, 0.4), (S, 0.6)], x + 7.5, CAP_TOP, CAP_H, LIGHT, 4.6 + LIGHT)
    g = (f'<path fill="none" stroke="{ink}" stroke-width="{HEAVY}" stroke-linecap="round" stroke-linejoin="round" d="{ceo}"/>'
         f'<path fill="none" stroke="{ink}" stroke-width="{LIGHT}" stroke-linecap="round" stroke-linejoin="round" d="{talks}"/>')
    return g, x


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(w)} {n(h)}" width="{n(w)}" height="{n(h)}" role="img">'
            f"<title>{title}</title>{body}</svg>\n")


def lockup(ink):
    g, end = wordmark(58, ink)
    return svg(end + 1, 48, mark() + g, "CEO Talks")


def main():
    out = SITE / "brand"
    out.mkdir(parents=True, exist_ok=True)
    (out / "mark.svg").write_text(svg(48, 48, mark(), "CEO Talks"), encoding="utf-8")
    (out / "logo.svg").write_text(lockup(CREAM), encoding="utf-8")
    (out / "logo-light.svg").write_text(lockup(DARK), encoding="utf-8")
    (SITE / "favicon.svg").write_text(svg(48, 48, mark(), "CEO Talks"), encoding="utf-8")
    for p in ("brand/mark.svg", "brand/logo.svg", "brand/logo-light.svg", "favicon.svg"):
        print("写好", p)


if __name__ == "__main__":
    main()
