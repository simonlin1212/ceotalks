// CEO Talks 网页：读 data/leaders.json（fetcher/leaders.py 写），首屏放最新一期，下面按人切换。
// 网址记着看什么：# 所有人（按时间分成 24 小时内 / 7 天 / 30 天 / 更早），#24h 只看 24 小时内，
// #who=jensen 只看一个人，两样可以叠（#24h&who=jensen）。人名栏翻下去也停在顶上，随时能切人。
// 中文版是根目录的 index.html，英文版是 en/index.html，两版共用这一份；看 <html lang> 用哪种文字。
// 时间按看的人自己电脑的时区显示。标题、简介是外面来的文字，一律当纯文字放，不当网页代码。
"use strict";

const EN = document.documentElement.lang === "en";
const ROOT = document.documentElement.dataset.root || "";   // 英文版在 en/ 下面，数据在上一层
const DATA_URL = `${ROOT}data/leaders.json`;
const REREAD = 5 * 60_000;     // 页面开着时每 5 分钟重读，切回这个标签页时也重读
const DAY = 24 * 3600_000;
const VID_RE = /^[A-Za-z0-9_-]{11}$/;
const KIND_EN = { 访谈: "Interview", 播客: "Podcast", 演讲: "Talk", 座谈: "Panel" };
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;

// 网页上会变的字，两种文字各一份；写死在网页里的字在两个 index.html 里
const T = EN ? {
  buckets: ["Last 24 hours", "Past 7 days", "Past 30 days", "Earlier"],
  bad: (what) => `leaders.json has an unexpected shape: ${what}`,
  ago: (m) => (m < 60 ? `${m} min ago` : m < 48 * 60 ? `${plural(Math.floor(m / 60), "hour", "hours")} ago`
    : `${plural(Math.floor(m / 1440), "day", "days")} ago`),
  approx: (s) => `about ${s}`,
  len: (h, m) => (h ? `${h}h ${m}m` : `${m} min`),
  views: (n) => `${new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(n)} ${n === 1 ? "view" : "views"}`,
  local: (iso) => new Date(iso).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: false }),
  date: (iso) => new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }),
  approxTip: "YouTube search only gave an approximate time",
  fresh: "New",
  unjudged: "Unreviewed",
  unjudgedTip: "Not checked by AI yet; listed because it comes from an official channel or an interview show",
  latest: "Latest",
  noData: (why) => `Couldn't load the data (${DATA_URL}): ${why}.`,
  loading: "Loading…",
  lede: (names, n) => `${names.join(", ")}${n > names.length ? ` and ${n - names.length} other leaders in AI and tech` : ""}, `
    + "speaking for themselves on podcasts, interviews, talks and panels. 20 minutes or longer, newest first. "
    + "No clips, reuploads or commentary.",
  stats: ["leaders", "long-form videos", "new in the last 24h"],
  updated: (t, a) => `Updated ${t} (${a})`,
  stale: (h) => `no update for ${h} hours`,
  aiFail: "AI review didn't run this round; official channels and interview shows are listed as “Unreviewed”",
  aiOff: "AI review is off; only official channels and interview shows are listed",
  reloadFail: (why) => `reload failed (${why}); showing the previous version`,
  errors: (n) => `${plural(n, "search", "searches")} incomplete this round`,
  everyone: "Everyone",
  everyoneAv: "All",
  count: (n) => plural(n, "video", "videos"),
  pStats: ["long-form videos", "latest video"],
  since: (ms) => ago(ms),
  none24: (name) => `No new long-form videos from ${name} in the last 24 hours. `,
  seeAllOf: (name) => `See all from ${name}`,
  noneOf: (name) => `No recent long-form videos from ${name} yet.`,
  none24All: (n) => `None of the ${n} leaders posted a new long-form video in the last 24 hours. `,
  seeAll: "See all",
  empty: "No data yet.",
} : {
  buckets: ["24 小时内", "最近 7 天", "最近 30 天", "更早"],
  bad: (what) => `leaders.json 结构不对：${what}`,
  ago: (m) => (m < 60 ? `${m} 分钟前` : m < 48 * 60 ? `${Math.floor(m / 60)} 小时前` : `${Math.floor(m / 1440)} 天前`),
  approx: (s) => `约 ${s}`,
  len: (h, m) => (h ? `${h} 小时 ${m} 分` : `${m} 分钟`),
  views: (n) => (n >= 10_000 ? `${(n / 10_000).toFixed(n >= 1_000_000 ? 0 : 1)} 万次观看` : `${n} 次观看`),
  local: (iso) => new Date(iso).toLocaleString("zh-CN", {
    month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false,
  }).replace(/\//g, "-"),
  date: (iso) => new Date(iso).toLocaleDateString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" }).replace(/\//g, "-"),
  approxTip: "YouTube 搜索页只给了大约时间，视频页还没开到",
  fresh: "24h 新",
  unjudged: "没判",
  unjudgedTip: "AI 没判过，先按官方频道或访谈节目放上来",
  latest: "最新一期",
  noData: (why) => `数据（${DATA_URL}）拿不到：${why}。先跑 python3 -I fetcher/leaders.py。`,
  loading: "在读……",
  lede: (names, n) => `${names.join("、")}等 ${n} 位 AI 与科技公司的领军人物，`
    + "本人亲自上的播客、访谈、演讲和座谈，20 分钟以上，新的在前。剪辑、搬运、别人转述的不收。",
  stats: ["位领军人物", "条长视频", "条 24 小时内新的"],
  updated: (t, a) => `上次更新 ${t}（${a}）`,
  stale: (h) => `${h} 小时没更新了`,
  aiFail: "AI 判这轮没通，官方频道和访谈节目先照放，标「没判」",
  aiOff: "没开 AI 判断，只放官方频道和访谈节目上的",
  reloadFail: (why) => `刚才重读失败（${why}），显示的是上一版`,
  errors: (n) => `这轮有 ${n} 处没取全`,
  everyone: "所有人",
  everyoneAv: "全",
  count: (n) => `${n} 条`,
  pStats: ["条长视频", "最近一条距今"],
  since: (ms) => ago(ms).replace("前", ""),
  none24: (name) => `${name} 24 小时内没有新的长视频。`,
  seeAllOf: (name) => `看${name}的全部`,
  noneOf: (name) => `最近没找到${name}本人讲的长视频。`,
  none24All: (n) => `24 小时内这 ${n} 位都没有新的长视频。`,
  seeAll: "看全部",
  empty: "还没有数据。",
};

let doc = null;       // 最近一次读到的数据（读失败保留上一版）
let why = "";         // 最近一次读失败的原因

/** 结构不对就抛错，页面保留上一版，不在画的时候白屏。 */
function validate(d) {
  const ok = (c, what) => { if (!c) throw new Error(T.bad(what)); };
  ok(!!d && typeof d === "object", "top");
  ok(!!d.meta && typeof d.meta.built === "string" && Array.isArray(d.meta.errors), "meta");
  ok(Array.isArray(d.people), "people");
  for (const p of d.people) {
    ok(!!p && typeof p.key === "string" && typeof p.zh === "string" && Array.isArray(p.videos), "people[]");
    for (const v of p.videos) {
      ok(!!v && typeof v.id === "string" && VID_RE.test(v.id) && !Number.isNaN(Date.parse(v.published))
        && typeof v.title === "string" && typeof v.duration === "number", `videos[] (${p.key})`);
    }
  }
}

let loading = false;
async function load() {
  if (loading) return;
  loading = true;
  try {
    const r = await fetch(DATA_URL, { cache: "no-store" });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    validate(d);
    doc = d;
    why = "";
  } catch (e) {
    why = e instanceof Error ? e.message : String(e);
  } finally {
    loading = false;
    render();
  }
}

// ---------- 小工具 ----------

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined && text !== null) n.textContent = String(text);
  return n;
}

const ago = (ms) => T.ago(Math.max(0, Math.floor(ms / 60_000)));

/** 一个月内说「几天前」，再早的直接写日期；搜索页只给了大约时间的标「约」。 */
function when(v, now) {
  const age = now - Date.parse(v.published);
  if (v.approx) return T.approx(ago(age));
  return age < 30 * DAY ? ago(age) : T.date(v.published);
}

function len(sec) {
  const m = Math.round(sec / 60);
  return T.len(Math.floor(m / 60), m >= 60 ? m % 60 : m);
}

const views = (n) => (n === null || n === undefined ? "" : T.views(n));

// 人名、头衔、类型按版本取；英文版没有对应英文的就不显示，不露中文
const nm = (p) => (EN ? p.en || p.zh : p.zh);
const rl = (p) => (EN ? p.role_en || "" : p.role);
const kind = (v) => (!v.kind || v.kind === "其他" ? "" : EN ? KIND_EN[v.kind] || "" : v.kind);

// 时间写在将来的不算（容 5 分钟钟差）
const isNew = (v, now) => { const age = now - Date.parse(v.published); return age > -300_000 && age < DAY; };

const $ = (id) => document.getElementById(id);

/** 网址里记着的筛选：只看 24 小时内？只看哪个人（空 = 所有人）？ */
function route() {
  const q = new URLSearchParams(location.hash.slice(1));
  return { only24: q.has("24h"), who: q.get("who") || "" };
}

function link(only24, who) {
  const parts = [];
  if (only24) parts.push("24h");
  if (who) parts.push(`who=${encodeURIComponent(who)}`);
  return parts.length ? `#${parts.join("&")}` : "#";
}

/** 没有照片，头像用英文名首尾两个词的首字母（Jensen Huang → JH）。 */
function avatar(p, size, fresh) {
  const w = String(p.en || p.key).split(/[\s-]+/).filter(Boolean);
  const s = el("span", `av ${size}`.trim(), ((w[0]?.[0] || "") + (w.length > 1 ? w[w.length - 1][0] : "")).toUpperCase());
  s.setAttribute("aria-hidden", "true");
  if (fresh) s.append(el("i", "dot"));
  return s;
}

/** 封面图。链接、图片地址都按视频编号自己拼，不用数据里的网址。 */
function thumb(v, fresh, big) {
  const th = el("span", big ? "thumb big" : "thumb");
  const img = el("img");
  img.alt = "";
  img.decoding = "async";
  img.referrerPolicy = "no-referrer";
  const hq = `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`;
  if (big) {
    // 首屏先试高清封面；有的视频没有，YouTube 会给 404 或一张很小的灰图，换回普通的
    const back = () => { if (img.src !== hq) img.src = hq; };
    img.addEventListener("error", back);
    img.addEventListener("load", () => { if (img.naturalWidth < 400) back(); });
    img.src = `https://i.ytimg.com/vi/${v.id}/maxresdefault.jpg`;
  } else {
    img.loading = "lazy";
    img.src = hq;
  }
  th.append(img, el("span", "len", len(v.duration)));
  if (fresh) th.append(el("span", "new", T.fresh));
  return th;
}

function ytLink(v, cls) {
  const a = el("a", cls);
  a.href = `https://www.youtube.com/watch?v=${v.id}`;
  a.target = "_blank";
  a.rel = "noreferrer noopener";
  return a;
}

function metaLine(v, now, withKind) {
  const m = el("span", "c-meta");
  if (withKind && kind(v)) m.append(el("span", "", kind(v)));
  m.append(el("span", "", v.channel));
  if (v.views) m.append(el("span", "", views(v.views)));
  const w = el("span", "", when(v, now));
  w.title = v.approx ? T.approxTip : T.local(v.published);
  m.append(w);
  return m;
}

/** 标题：中文版放 AI 写的中文标题 + 原标题 + 一句话简介；英文版只放原标题。 */
function titles(a, v, cls) {
  if (EN) return a.append(el("span", cls.t, v.title));
  a.append(el("span", cls.t, v.zh || v.title));
  if (v.zh) a.append(el("span", cls.o, v.title));
  if (v.gist) a.append(el("span", cls.g, v.gist));
}

function card(v, p, now, showWho) {
  const a = ytLink(v, "card");
  a.append(thumb(v, isNew(v, now), false));
  const who = el("span", "c-who");
  if (showWho) who.append(avatar(p, "sm"), el("span", "c-name", nm(p)));
  if (kind(v)) who.append(el("span", "c-kind", kind(v)));
  if (!v.judged) {
    const k = el("span", "tag", T.unjudged);
    k.title = T.unjudgedTip;
    who.append(k);
  }
  if (who.childNodes.length) a.append(who);
  titles(a, v, { t: "c-t", o: "c-o", g: "c-g" });
  a.append(metaLine(v, now, false));
  return a;
}

function feature(v, p, now) {
  const a = ytLink(v, "feat");
  const label = el("span", "feat-label");
  label.append(el("span", "live"), `${T.latest} · ${when(v, now)}`);
  const th = thumb(v, false, true);
  th.append(el("span", "play"));
  const who = el("span", "who");
  const names = el("span");
  names.append(el("b", "", nm(p)), el("small", "", (EN ? [rl(p)] : [p.en, p.role]).filter(Boolean).join(" · ")));
  who.append(avatar(p, "lg"), names);
  a.append(label, th, who);
  titles(a, v, { t: "feat-t", o: "feat-o", g: "feat-g" });
  a.append(metaLine(v, now, true));
  return a;
}

function stat(n, label, hot) {
  const d = el("div", hot ? "hot" : "");
  d.append(el("dt", "", label), el("dd", "", n));
  return d;
}

// ---------- 画页面 ----------

const langBase = $("lang").getAttribute("href");

function render() {
  const now = Date.now();
  const { only24 } = route();
  let { who } = route();

  for (const a of $("seg").querySelectorAll("a")) a.classList.toggle("on", (a.dataset.v === "24h") === only24);
  $("lang").href = langBase + (location.hash.length > 1 ? location.hash : "");   // 换语言时停在同一个人、同一个时间段

  if (!doc) {
    $("status").textContent = why ? T.noData(why) : T.loading;
    return;
  }

  const people = doc.people.map((p) => ({
    ...p, videos: [...p.videos].sort((a, b) => Date.parse(b.published) - Date.parse(a.published)),
  }));
  // 刚讲过话的人排在前面；都没有的按名单顺序放最后
  people.sort((a, b) => (Date.parse(b.videos[0]?.published ?? "") || 0) - (Date.parse(a.videos[0]?.published ?? "") || 0));
  const person = people.find((p) => p.key === who);
  if (!person) who = "";   // 名单里没有这个人（比如旧链接）就看所有人
  const pick = person ? [person] : people;
  const inMode = (p) => (only24 ? p.videos.filter((v) => isNew(v, now)) : p.videos);
  const all = people.flatMap((p) => p.videos.map((v) => ({ v, p })))
    .sort((a, b) => Date.parse(b.v.published) - Date.parse(a.v.published));
  const fresh = all.filter(({ v }) => isNew(v, now)).length;

  for (const a of $("seg").querySelectorAll("a")) a.href = link(a.dataset.v === "24h", who);   // 切时间不丢选中的人
  const n24 = pick.reduce((s, p) => s + p.videos.filter((v) => isNew(v, now)).length, 0);
  $("n24").textContent = n24;
  $("n24").className = n24 ? "" : "zero";

  // 首屏：一句话、三个数、更新时间、最新一期
  $("lede").textContent = T.lede(doc.people.slice(0, 3).map(nm), people.length);
  $("stats").replaceChildren(stat(people.length, T.stats[0]), stat(all.length, T.stats[1]), stat(fresh, T.stats[2], fresh > 0));

  const m = doc.meta;
  const staleH = (now - Date.parse(m.built)) / 3600_000;
  const st = $("status");
  st.className = "status" + (staleH > 8 ? " stale" : "");
  let line = T.updated(T.local(m.built), ago(now - Date.parse(m.built)));
  if (staleH > 8) line += ` · ${T.stale(Math.floor(staleH))}`;
  if (m.ai === false) line += ` · ${T.aiFail}`;
  if (m.ai === null && m.aiProvider === "off") line += ` · ${T.aiOff}`;
  if (why) line += ` · ${T.reloadFail(why)}`;
  st.textContent = line;
  if (m.errors.length) {
    const s = el("span", "", T.errors(m.errors.length));
    if (!EN) s.title = m.errors.join("\n");   // 抓取端写的出错原因是中文，英文版不挂
    st.append(" · ", s);
  }
  $("feature").replaceChildren(...(all.length ? [feature(all[0].v, all[0].p, now)] : []));

  // 人名栏：第一个「所有人」，后面每人一个，点了只看这个人。头像上的橙点 = 24 小时内有新的
  const chip = (key, label, count, av) => {
    const a = el("a", "chip" + (key === who ? " sel" : "") + (count ? "" : " zero"));
    a.href = link(only24, key);
    if (key === who) a.setAttribute("aria-current", "true");
    a.append(av, label, el("small", "", count));
    return a;
  };
  const allAv = el("span", "av all", T.everyoneAv);
  allAv.setAttribute("aria-hidden", "true");
  $("chips").replaceChildren(
    chip("", T.everyone, people.reduce((s, p) => s + inMode(p).length, 0), allAv),
    ...people.map((p) => chip(p.key, nm(p), inMode(p).length, avatar(p, "", p.videos.some((v) => isNew(v, now))))),
  );

  // 下面的列表
  const feed = [];
  const empty = (text, to, label) => {
    const e = el("p", "empty", text);
    if (to) { const a = el("a", "", label); a.href = to; e.append(a); }
    return e;
  };
  if (person) {
    const vids = inMode(person);
    const head = el("section", "profile");
    const txt = el("div");
    if (!EN) txt.append(el("p", "en", person.en));
    txt.append(el("h2", "", nm(person)), el("p", "role", rl(person)));
    const ps = el("dl", "p-stats");
    ps.append(stat(person.videos.length, T.pStats[0]),
      stat(person.videos.length ? T.since(now - Date.parse(person.videos[0].published)) : "—", T.pStats[1]));
    head.append(avatar(person, "xl"), txt, ps);
    feed.push(head);
    if (vids.length) {
      const g = el("div", "grid");
      g.append(...vids.map((v) => card(v, person, now, false)));
      feed.push(g);
    } else if (only24) {
      feed.push(empty(T.none24(nm(person)), link(false, who), T.seeAllOf(nm(person))));
    } else {
      feed.push(empty(T.noneOf(nm(person))));
    }
  } else {
    const items = only24 ? all.filter(({ v }) => isNew(v, now)) : all;
    let from = -Infinity;   // 时间写在将来的（钟差）也放进第一段，不丢
    for (const [i, upto] of [DAY, 7 * DAY, 30 * DAY, Infinity].entries()) {
      const part = items.filter(({ v }) => { const age = now - Date.parse(v.published); return age >= from && age < upto; });
      from = upto;
      if (!part.length) continue;
      const sec = el("section", "bucket");
      const h = el("header", "b-head");
      h.append(el("h2", "", T.buckets[i]), el("span", "", T.count(part.length)));
      const g = el("div", "grid");
      g.append(...part.map(({ v, p }) => card(v, p, now, true)));
      sec.append(h, g);
      feed.push(sec);
    }
    if (!feed.length) {
      feed.push(only24 ? empty(T.none24All(people.length), link(false, ""), T.seeAll) : empty(T.empty));
    }
  }
  $("feed").replaceChildren(...feed);

  // 关于里的名单，按 people.json 里的顺序
  $("roster").replaceChildren(...doc.people.map((p) => {
    const a = el("a");
    a.href = link(false, p.key);
    a.append(avatar(p, "sm"), nm(p), el("small", "", rl(p)));
    return a;
  }));
  arrows();
}

// ---------- 顶栏、人名栏 ----------

const topH = () => document.querySelector(".site").offsetHeight;

/** 人名栏贴到顶栏下面时加底色，没贴住时跟页面融在一起。 */
function stick() {
  const bar = $("bar");
  bar.classList.toggle("stuck", bar.getBoundingClientRect().top <= topH() + 0.5);
}

function measure() {
  document.documentElement.style.setProperty("--toph", `${topH()}px`);
  stick();
  arrows();
}

/** 人名栏放不下时两头出箭头（手机上靠手指滑，不出）。 */
function arrows() {
  const c = $("chips");
  $("arr-l").hidden = c.scrollLeft <= 2;
  $("arr-r").hidden = c.scrollLeft + c.clientWidth >= c.scrollWidth - 2;
}

/** 把选中的人挪到人名栏看得见的地方。 */
function showSel() {
  const chips = $("chips");
  const sel = chips.querySelector(".sel");
  if (sel && chips.scrollWidth > chips.clientWidth) {
    chips.style.scrollBehavior = "auto";
    chips.scrollLeft = sel.offsetLeft - (chips.clientWidth - sel.offsetWidth) / 2;
    chips.style.scrollBehavior = "";
  }
  arrows();
}

window.addEventListener("hashchange", () => {
  render();
  showSel();
  // 切了人或时间：滚到列表开头，人名栏停在顶上
  const y = Math.max(0, $("feed").getBoundingClientRect().top + window.scrollY - topH() - $("bar").offsetHeight + 1);
  if (Math.abs(window.scrollY - y) > 4) window.scrollTo({ top: y, behavior: Math.abs(window.scrollY - y) < 1400 ? "smooth" : "auto" });
});
document.querySelector(".logo").addEventListener("click", (e) => {
  e.preventDefault();
  if (location.hash) history.pushState(null, "", location.pathname + location.search);
  render();
  showSel();
  window.scrollTo({ top: 0, behavior: "smooth" });
});
$("go-about").addEventListener("click", () => $("about").scrollIntoView({ behavior: "smooth" }));
$("arr-l").addEventListener("click", () => $("chips").scrollBy({ left: -$("chips").clientWidth * 0.7 }));
$("arr-r").addEventListener("click", () => $("chips").scrollBy({ left: $("chips").clientWidth * 0.7 }));
$("chips").addEventListener("scroll", arrows, { passive: true });
window.addEventListener("scroll", stick, { passive: true });
window.addEventListener("resize", measure);
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") load(); });
setInterval(() => { if (document.visibilityState === "visible") load(); }, REREAD);
setInterval(render, 60_000);   // 「几分钟前」「24 小时内」每分钟重算
measure();
load().then(showSel);
