# 更新日志

## v1.0.0（2026-10-28）

第一个版本：13 位 AI 与科技公司领军人物，本人亲口讲的长视频，抓取端 + 中英双语静态网站。

### 新增

- **抓取端**（`fetcher/`，只用 Python 3.9 自带库，不用 YouTube key）：每人搜两次 YouTube（引号里的全名、全名加 interview；本周上传、20 分钟以上），按名字和头衔认候选；只给要放上页面的打开视频页拿准确时间和时长，一轮最多 30 个、每次隔 2 秒，碰到 429 或人机验证，这一轮就不再请求 YouTube。
- **累积库**（`data/store.json`）：判过的不重判，留 400 天；先写临时文件再换名，读不了的库挪成 `store.json.bad-时间` 留着（GitHub Actions 上改成直接停）；同一时间只跑一轮（文件锁）。
- **AI 判断三选一**：`off`（默认，只放认得的官方频道和访谈节目上的，标「没判」）、`openai`（任何 OpenAI 兼容接口）、`command`（任何本机命令，如 Claude Code、Codex 命令行）。顺带写中文标题和一句话简介、去掉同一场的重复；key 只从环境变量或 key 文件读，出错信息先抹掉再记（设的 key、环境变量里名字以 KEY / TOKEN / SECRET / PASSWORD 结尾的值、`Bearer` 后面那段、`api_key=值` 和 `--api-key 值` 这类写法、`sk-` 开头的）；带 key 的接口要用 https（本机除外）、不跟跳转；连着两批不通（没回，或一条能用的都没有）这一轮就不再叫。
- **名单**（`fetcher/people.json`）：13 位人物的中英文名和头衔、认名字的规则、认的官方频道和访谈节目；加人删人不改代码。
- **网站**（`site/`，纯静态）：中文版 `/`、英文版 `/en/`，右上角切换并停在同一个人；首屏最新一期，所有人按「24 小时内 / 最近 7 天 / 最近 30 天 / 更早」分段，可按人看、只看 24 小时内，网址记着看什么；开着时每 5 分钟重读数据；各自的分享图、`canonical`、`hreflang`。
- **设置**：`LEADERS_AI_MAX_TOKENS`（回答最长多少 token，Cloudflare Workers AI 默认只给 256，要设）、`LEADERS_MAX_PAGES`（一轮最多开几个视频页，机房的机器上设 0）。
- **线上更新**（`.github/workflows/update-site.yml` + `deploy/`）：GitHub Actions 每 2 小时跑一轮，取 `data` 分支上的累积库 → 抓 → 叫 AI 判（任何 OpenAI 兼容接口，地址、模型、key 都在仓库设置里）→ 存回 `data` 分支 → 用 wrangler 传到 Cloudflare Workers；也能手动点，选只跑某几个人、关 AI、不存、不传。GitHub 的机器开不了 YouTube 视频页，这条路上不开（时间是大约的）。只有确认还没有 `data` 分支才按空库起；取不到、读不了库，或跑完条数掉一半以上，这一轮就停、不存不传。两个 action 按提交号固定，wrangler 照 `deploy/package-lock.json` 装。
- **命令**：`--backfill`（第一次填库，搜今年）、`--only`（只跑某几个人）、`--page-only`（不搜、不叫 AI，只重出页面数据）、`check_ai.py`（换 AI 前对一批判法，不改库）、`dev/serve.mjs`（本机预览）。
- **标志和分享图**：`brand/make_logo.py` 画标志，`brand/make_images.sh` 用本机 Chrome 截中英文分享图和手机图标。

### 测试

- `tests/test_offline.py` 不联网 19 条：认名字、AI 回话的几种格式、同一场去重、认不出的回话留原话、两种 AI 接法、回答长度设置、key 不出现在报错里、接口跳转不跟、带 key 不许远程 http、本机命令报错和超时不露 key、常见的 key 写法都抹掉、本机模型不要 key、设置不对时的报错、AI 一条能用的都没回算这批不通、AI 关着时只放哪些、每个人中英文头衔都有。
