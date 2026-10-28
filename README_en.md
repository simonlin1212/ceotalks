<p align="center"><a href="README.md">简体中文</a> | <b>English</b></p>

<h1 align="center">CEO Talks</h1>

<p align="center">
  <b>Long-form videos where the leaders of AI and tech companies speak for themselves</b><br>
  13 leaders · podcasts / interviews / talks / panels · 20+ minutes · the person on camera only · bilingual site · no YouTube API key · zero dependencies
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/badge/license-Apache%202.0-blue"></a>
  <a href="CHANGELOG.md"><img alt="Source v1.0.0" src="https://img.shields.io/badge/source-v1.0.0-F35D2B"></a>
  <img alt="13 leaders" src="https://img.shields.io/badge/leaders-13-2f9e44">
  <img alt="Python 3.9+, standard library only" src="https://img.shields.io/badge/python-3.9%2B%20stdlib-3776AB">
  <img alt="No YouTube API key" src="https://img.shields.io/badge/YouTube%20API%20key-not%20needed-success">
  <img alt="AI: Claude Code, Codex, OpenAI-compatible API, or off" src="https://img.shields.io/badge/AI-Claude%20Code%20%7C%20Codex%20%7C%20API%20%7C%20off-black">
</p>

---

<p align="center">
  <a href="#screenshots">Screenshots</a> ·
  <a href="#who-and-what-is-included">Coverage</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#ai-judging">AI Judging</a> ·
  <a href="#reference">Reference</a> ·
  <a href="#how-it-works">How It Works</a> ·
  <a href="#deploying">Deploying</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="CHANGELOG.md">Changelog</a>
</p>

<p align="center"><img src="site/brand/og.png" width="760" alt="CEO Talks"></p>

Musk, Jensen Huang, Lisa Su, Altman, Hassabis: they show up on YouTube many times a week, but most of those videos are other people talking about them. Commentary, clips, reuploads, dubbed translations.
CEO Talks searches YouTube on a schedule for everyone on the list, **keeps only long videos where the person is actually on camera speaking**, builds up an ever-growing archive, and generates a bilingual static website: the latest episode up top, then everything grouped by time, filterable by person or by the last 24 hours.

- **13 leaders of AI and tech companies**: Elon Musk, Jensen Huang, Lisa Su, Lip-Bu Tan, Fei-Fei Li, Sundar Pichai, Demis Hassabis, Dario Amodei, Sam Altman, Mark Zuckerberg, Satya Nadella, Ilya Sutskever, Andrej Karpathy. The list is a single JSON file; add or remove people without touching code.
- **Only the person themselves**: podcasts they appear on, long interviews, keynotes, fireside chats and panels, 20 minutes or longer. Commentary about them, news analysis, clip compilations, reuploads, AI voice-overs and dubbed translations are all left out.
- **Pluggable AI, or none**: use the local Claude Code or Codex CLI, or any OpenAI-compatible API (OpenAI, DeepSeek, OpenRouter, Zhipu, a local Ollama, and so on). With AI off it still runs, showing only recognized official channels and interview shows.
- **Bilingual site**: the Chinese version lives at `/`, with AI-written Chinese titles and one-line summaries; the English version lives at `/en/` and shows the original YouTube titles. One click in the top-right corner switches language and keeps you on the same person.
- **Nothing to install**: the fetcher uses only the Python 3.9 standard library. No `pip install`, no YouTube API key. The site is plain HTML + CSS + JS with no build step; drop it on any static host.
- **The archive keeps growing**: judged videos are stored in a local database, never judged twice, and kept for 400 days. Each run only sends newly found candidates to the AI.

> Current version v1.0.0 (2026-10-28): first release. Fetcher, bilingual site, three ways to plug in AI, 14 offline tests.

---

## Screenshots

<table>
<tr>
<td width="62%" valign="top"><img src="assets/screenshots/2026-10-28/home-en.jpg" alt="English home page"><br><b>English home page</b>: a one-line description, three counters, last update time, the latest episode as a large card, then the people bar and the time-grouped list</td>
<td width="38%" valign="top"><img src="assets/screenshots/2026-10-28/mobile-zh.jpg" alt="On a phone"><br><b>On a phone</b> (Chinese version): the people bar scrolls sideways and stays pinned to the top</td>
</tr>
<tr>
<td colspan="2"><img src="assets/screenshots/2026-10-28/home-zh.jpg" alt="Chinese home page"><br><b>Chinese version</b>: adds a Chinese title, the original title and a one-line summary to each video</td>
</tr>
</table>

> Video thumbnails are blanked out in these screenshots: thumbnails belong to the video creators. On the live site the visitor's browser loads them straight from YouTube; they are never stored in this repository.

What the site does:

- **Header**: one line on what this is, three counters (leaders / long-form videos / new in the last 24 hours), the last update time, and the latest episode shown large.
- **People bar**: "Everyone" plus the 13 leaders, pinned to the top while you scroll. An orange dot on an avatar means that person has something new in the last 24 hours.
- **List**: with "Everyone" selected, videos are grouped into "Last 24 hours / Past 7 days / Past 30 days / Earlier". Pick a person to see only theirs.
- **Each video**: thumbnail and length, a "New" badge for the last 24 hours, the type (Podcast / Interview / Talk / Panel), channel, views and how long ago it was published. The Chinese version adds a Chinese title, the original title and a one-line summary. Videos the AI hasn't judged are marked "Unreviewed".
- **Time**: within a month it shows "x min / hours / days ago", older than that the date. Times that are only approximate read "about …". Hover over an exact time to see the date and clock time in the visitor's own time zone.
- **The URL remembers the view**: `#` everyone, `#24h` last 24 hours only, `#who=jensen` one person; they combine (`#24h&who=jensen`), so every person has a shareable link.
- **Stays fresh**: while the page is open it re-reads the data every 5 minutes, and again when you switch back to the tab. If there's been no update for more than 8 hours, the update line says so. If the AI failed on a run, the page says the official-channel and interview-show videos are listed as "Unreviewed".
- **Sharing and search**: each version has its own share image, `canonical` and `hreflang`, and the two point at each other as the Chinese and English versions of the same page.

## Who and what is included

<table>
<tr><th nowrap>URL key</th><th nowrap>Leader</th><th>Title (English site)</th></tr>
<tr><td nowrap><code>musk</code></td><td nowrap>Elon Musk</td><td>Tesla · SpaceX · xAI</td></tr>
<tr><td nowrap><code>jensen</code></td><td nowrap>Jensen Huang</td><td>NVIDIA CEO</td></tr>
<tr><td nowrap><code>lisasu</code></td><td nowrap>Lisa Su</td><td>AMD CEO</td></tr>
<tr><td nowrap><code>lipbutan</code></td><td nowrap>Lip-Bu Tan</td><td>Intel CEO</td></tr>
<tr><td nowrap><code>feifei</code></td><td nowrap>Fei-Fei Li</td><td>World Labs co-founder · Stanford professor</td></tr>
<tr><td nowrap><code>sundar</code></td><td nowrap>Sundar Pichai</td><td>Google / Alphabet CEO</td></tr>
<tr><td nowrap><code>demis</code></td><td nowrap>Demis Hassabis</td><td>Google DeepMind CEO</td></tr>
<tr><td nowrap><code>dario</code></td><td nowrap>Dario Amodei</td><td>Anthropic CEO</td></tr>
<tr><td nowrap><code>altman</code></td><td nowrap>Sam Altman</td><td>OpenAI CEO</td></tr>
<tr><td nowrap><code>zuck</code></td><td nowrap>Mark Zuckerberg</td><td>Meta CEO</td></tr>
<tr><td nowrap><code>satya</code></td><td nowrap>Satya Nadella</td><td>Microsoft CEO</td></tr>
<tr><td nowrap><code>ilya</code></td><td nowrap>Ilya Sutskever</td><td>SSI co-founder</td></tr>
<tr><td nowrap><code>karpathy</code></td><td nowrap>Andrej Karpathy</td><td>Former Director of AI at Tesla</td></tr>
</table>

**Included**: the person speaks on camera, the video is 20 minutes or longer, and it falls into one of four types:

<table>
<tr><th nowrap>Type</th><th>What counts</th></tr>
<tr><td nowrap>Podcast</td><td>The person is a guest on someone else's podcast</td></tr>
<tr><td nowrap>Interview</td><td>A long one-on-one interview with a journalist or host</td></tr>
<tr><td nowrap>Talk</td><td>The person alone on stage: a keynote or lecture</td></tr>
<tr><td nowrap>Panel</td><td>Fireside chats, roundtables, multi-person conversations on stage</td></tr>
</table>

**Not included**: videos about the person by someone else (news analysis, commentary, reactions, gossip, documentaries, biographies, stock analysis, a mention in a weekly news roundup), clickbait that only uses their name, AI voice-overs or dubbed translations, clip compilations, the same interview or talk reuploaded by another channel (live streams from official channels and major media are fine), uploads by translation channels, subtitle groups, English-learning channels or content farms, family members or colleagues who share the surname, and anything under 20 minutes. When unsure, it's left out. When the same event appears several times, only the original or official upload is kept.

## Quick Start

Requires Python 3.9+ on macOS or Linux (on Windows use WSL; the file lock uses Unix `fcntl`). The machine needs to reach YouTube (the system `HTTPS_PROXY` is used by default).

**1. Clone**

```bash
git clone https://github.com/simonlin1212/ceotalks.git
cd ceotalks
```

**2. Run one round** (AI off, a few minutes)

```bash
python3 -I fetcher/leaders.py
```

To fill the archive on the first run, search this year's uploads (normal runs search this week's):

```bash
python3 -I fetcher/leaders.py --backfill
```

**3. Open the site locally**, then visit http://127.0.0.1:8860/ (English version at http://127.0.0.1:8860/en/)

```bash
node dev/serve.mjs 8860
```

No Node? This works too:

```bash
python3 -I -m http.server 8860 --bind 127.0.0.1 --directory site
```

**4. Turn on AI judging** (recommended, see the next section). You'll get far more videos.

## AI Judging

The AI decides for each candidate whether "the person is actually speaking in it", and also writes a Chinese title and a one-line summary and removes duplicates of the same event.

**With AI off**, only videos from **official company channels** listed in `people.json` (they must carry the verified badge) and from two **guest-only interview shows** (Lex Fridman, Dwarkesh Patel) make it onto the page, marked "Unreviewed". That's a lot less content. Measured from an empty archive: one round found 142 candidates for the 13 people, and with AI off only 2 reached the page (both Jensen Huang on NVIDIA's official channel); nobody else had any.

**With AI on**, judged videos are stored and never judged again. Each run only sends new candidates, 8 per batch, so it uses few tokens.

Setup: copy `config.example.env` to `config.env` (already in `.gitignore`, never committed), edit it, then `source config.env` before running.

<table>
<tr><th nowrap><code>LEADERS_AI</code></th><th>What it uses</th><th>What to set</th></tr>
<tr><td nowrap><code>off</code> (default)</td><td>No AI</td><td>—</td></tr>
<tr><td nowrap><code>openai</code></td><td>Any OpenAI-compatible chat API (<code>/chat/completions</code>)</td><td><code>LEADERS_AI_URL</code> (defaults to OpenAI), <code>LEADERS_AI_MODEL</code> (required); put the key in <code>LEADERS_AI_KEY</code>, or in a file pointed to by <code>LEADERS_AI_KEY_FILE</code>; local models can skip the key</td></tr>
<tr><td nowrap><code>command</code></td><td>Any local command that reads the prompt from stdin and writes the answer to stdout, such as Claude Code, the Codex CLI, or your own script</td><td><code>LEADERS_AI_CMD</code>, the full command</td></tr>
</table>

Example: one round with the local Codex CLI

```bash
LEADERS_AI=command LEADERS_AI_CMD="codex exec --skip-git-repo-check -s read-only -" LEADERS_AI_TIMEOUT=300 python3 -I fetcher/leaders.py
```

Example: any OpenAI-compatible API (swap in your provider's URL and model name)

```bash
LEADERS_AI=openai LEADERS_AI_URL=https://api.openai.com/v1/chat/completions LEADERS_AI_MODEL=your-model LEADERS_AI_KEY_FILE=~/.config/leaders/ai.key python3 -I fetcher/leaders.py
```

- **Keys**: read fresh from the environment variable or key file only, never written into code, logs or output; error messages have the key scrubbed first. Keys containing spaces, newlines or non-ASCII characters are rejected outright.
- **When the AI is down**: if a batch fails it tries the next one; after two failed batches in a row it stops calling the AI for that run, and unjudged videos wait for the next run while official channels and interview shows are shown provisionally. A video that gets no answer three times is only retried once a day after that. If the AI's reply can't be read as JSON, the raw reply is saved to `data/ai_bad_last.txt` for inspection.
- **Titles and descriptions are treated as material**: the prompt tells the AI not to follow any instructions found in a video's title or description.
- **Compare before switching AI**: `check_ai.py` picks judged videos from the archive (half kept, half rejected, newest first), has the currently configured AI judge them again, and lists each one as same or different. It never changes the archive (an unreadable AI reply is saved to `data/ai_bad_check.txt`).

```bash
python3 -I fetcher/check_ai.py --n 16
```

## Reference

### Commands

<table>
<tr><th nowrap>Command</th><th>What it does</th></tr>
<tr><td nowrap><code>python3 -I fetcher/leaders.py</code></td><td>One round: search this week's uploads, judge, verify times, write the archive, output page data</td></tr>
<tr><td nowrap><code>  --backfill</code></td><td>Search this year's uploads (for the first fill)</td></tr>
<tr><td nowrap><code>  --ai off|openai|command</code></td><td>Use a different AI for this run only; otherwise <code>LEADERS_AI</code> decides</td></tr>
<tr><td nowrap><code>  --only jensen,lisasu</code></td><td>Search only these people (keys from the table above); other people's videos still waiting for the AI or a video page are processed as usual</td></tr>
<tr><td nowrap><code>  --page-only</code></td><td>No search, no AI: rebuild the page data from the archive (after editing names or titles in the list); the update time stays that of the last real run</td></tr>
<tr><td nowrap><code>python3 -I fetcher/check_ai.py</code></td><td>Compare judgments before switching AI; <code>--n</code> how many (default 16), <code>--ai openai|command</code> to override</td></tr>
<tr><td nowrap><code>node dev/serve.mjs [port]</code></td><td>Preview the site locally; default 8860, listens on 127.0.0.1 only, no caching</td></tr>
<tr><td nowrap><code>python3 -I tests/test_offline.py</code></td><td>14 offline tests</td></tr>
<tr><td nowrap><code>python3 -I brand/make_logo.py</code></td><td>Redraw the logo: writes <code>mark.svg</code>, <code>logo.svg</code>, <code>logo-light.svg</code> under <code>site/brand/</code> and <code>site/favicon.svg</code></td></tr>
<tr><td nowrap><code>zsh brand/make_images.sh</code></td><td>Render the Chinese and English share images and app icons with the local Chrome (macOS Chrome path)</td></tr>
</table>

Exit codes: `0` normal (including "another round is still running, skipped"); `2` bad arguments or AI settings (for example an unknown person key, or `openai` without a model name). `check_ai.py` exits with `2` when AI is off, and fails with an error (`1`) when there's no archive yet or the AI settings are wrong.

### Settings (environment variables)

<table>
<tr><th nowrap>Variable</th><th nowrap>Default</th><th>Notes</th></tr>
<tr><td nowrap><code>LEADERS_AI</code></td><td nowrap><code>off</code></td><td>Which AI: <code>off</code> / <code>openai</code> / <code>command</code></td></tr>
<tr><td nowrap><code>LEADERS_AI_URL</code></td><td nowrap>OpenAI</td><td>API endpoint for <code>openai</code>; must start with <code>http://</code> or <code>https://</code>; default <code>https://api.openai.com/v1/chat/completions</code></td></tr>
<tr><td nowrap><code>LEADERS_AI_MODEL</code></td><td nowrap>—</td><td>Required for <code>openai</code></td></tr>
<tr><td nowrap><code>LEADERS_AI_KEY</code></td><td nowrap>—</td><td>API key; optional for local models</td></tr>
<tr><td nowrap><code>LEADERS_AI_KEY_FILE</code></td><td nowrap>—</td><td>File containing only the key; read when <code>LEADERS_AI_KEY</code> isn't set</td></tr>
<tr><td nowrap><code>LEADERS_AI_CMD</code></td><td nowrap>—</td><td>Full command to run for <code>command</code></td></tr>
<tr><td nowrap><code>LEADERS_AI_TIMEOUT</code></td><td nowrap><code>180</code></td><td>Seconds to wait for one AI call</td></tr>
<tr><td nowrap><code>LEADERS_AI_MAX_TOKENS</code></td><td nowrap>not sent</td><td>For <code>openai</code>: the longest answer, in tokens. Some endpoints default to too little to finish a batch (Cloudflare Workers AI defaults to 256); set it to about <code>4096</code></td></tr>
<tr><td nowrap><code>LEADERS_DATA</code></td><td nowrap><code>data/</code></td><td>Where the archive <code>store.json</code>, the lock file and unreadable AI replies go</td></tr>
<tr><td nowrap><code>LEADERS_OUT</code></td><td nowrap><code>site/data/leaders.json</code></td><td>Where the page data is written</td></tr>
<tr><td nowrap><code>LEADERS_PEOPLE</code></td><td nowrap><code>fetcher/people.json</code></td><td>Which list to use</td></tr>
<tr><td nowrap><code>LEADERS_NO_PROXY</code></td><td nowrap>unset</td><td>Unset: follow the system <code>HTTPS_PROXY</code>; set to <code>1</code> to force a direct connection</td></tr>
<tr><td nowrap><code>LEADERS_MAX_PAGES</code></td><td nowrap><code>30</code></td><td>The most video pages to open per run (for exact times and full descriptions); <code>0</code> = none. Data-center machines (GitHub Actions, cloud servers) get a bot check on the very first video page, so set <code>0</code> there; times on the site then stay approximate</td></tr>
</table>

### The list (`fetcher/people.json`)

Adding or removing people, or changing titles, only touches this file. One entry per person:

<table>
<tr><th nowrap>Field</th><th>Meaning</th></tr>
<tr><td nowrap><code>key</code></td><td>The name used in URLs, e.g. <code>#who=jensen</code>; lowercase letters, digits and underscores only</td></tr>
<tr><td nowrap><code>zh</code> / <code>en</code></td><td>Chinese name / English name (searches use the full English name)</td></tr>
<tr><td nowrap><code>role</code> / <code>role_en</code></td><td>Title shown on the Chinese / English site</td></tr>
<tr><td nowrap><code>names</code></td><td>Names that count as this person in a title or description (full name, surname); spaces and hyphens are optional (Fei-Fei Li / Fei Fei Li / FeiFei Li)</td></tr>
<tr><td nowrap><code>titles</code></td><td>Titles that also count (e.g. <code>Nvidia CEO</code>; <code>Nvidia's CEO</code> matches too)</td></tr>
<tr><td nowrap><code>short</code> + <code>short_ctx</code></td><td>First-name-only form (e.g. <code>jensen</code>); it counts only if <code>short_ctx</code> also matches the title or snippet. <code>short_ctx</code> is a regex matched against lowercase text, alternatives separated by <code>|</code>, e.g. <code>nvidia|huang|gtc</code></td></tr>
<tr><td nowrap><code>same_surname</code></td><td>Family members and colleagues with the same surname, as a regex matched against lowercase text (e.g. <code>\b(kimbal|maye)\b</code>); a surname match that also matches one of these names but lacks the person's first name doesn't count</td></tr>
</table>

Two more tables: `official_channels` (official company channel names, counted only with the verified badge) and `interview_channels` (recognized interview shows, matched by channel ID, since anyone can pick a display name).

### Built-in limits

<table>
<tr><th nowrap>Rule</th><th>Value</th></tr>
<tr><td nowrap>Searches per person per round</td><td>2: the full name in quotes, and the full name plus "interview" (searching the name alone often returns 20 results of other people's commentary)</td></tr>
<tr><td nowrap>Minimum length</td><td>20 minutes (filtered at search time, and again after checking the video page)</td></tr>
<tr><td nowrap>Search window</td><td>Uploaded this week; this year with <code>--backfill</code></td></tr>
<tr><td nowrap>Request pace</td><td>One at a time; 2 seconds between searches and between video pages</td></tr>
<tr><td nowrap>Video pages</td><td>At most 30 opened per round, the rest next round; a page that fails 3 times isn't tried again and keeps its approximate time</td></tr>
<tr><td nowrap>Blocked</td><td>On a 429 or a bot check the round makes no more YouTube requests; whatever wasn't searched or opened waits for the next round, and what was already found is still judged and written out</td></tr>
<tr><td nowrap>AI batch</td><td>8 videos, plus this person's 8 most recent kept videos to spot duplicates of the same event</td></tr>
<tr><td nowrap>Archive retention</td><td>400 days</td></tr>
<tr><td nowrap>Videos per person on the page</td><td>The latest 20</td></tr>
<tr><td nowrap>Concurrency</td><td>One round at a time (file lock); if another round is running, this one is skipped</td></tr>
</table>

## Usage Examples

<table>
<tr><th nowrap>I want to…</th><th>Do this</th></tr>
<tr><td nowrap>Try it the first time</td><td><code>python3 -I fetcher/leaders.py --backfill</code>, then <code>node dev/serve.mjs</code> and open http://127.0.0.1:8860/</td></tr>
<tr><td nowrap>Judge with the local Codex CLI</td><td><code>LEADERS_AI=command LEADERS_AI_CMD="codex exec --skip-git-repo-check -s read-only -" LEADERS_AI_TIMEOUT=300 python3 -I fetcher/leaders.py</code></td></tr>
<tr><td nowrap>Judge with the local Claude Code</td><td><code>LEADERS_AI=command LEADERS_AI_CMD="claude -p" python3 -I fetcher/leaders.py</code></td></tr>
<tr><td nowrap>Judge with an API provider</td><td>Set <code>LEADERS_AI=openai</code>, <code>LEADERS_AI_URL</code>, <code>LEADERS_AI_MODEL</code> and <code>LEADERS_AI_KEY_FILE</code> in <code>config.env</code>, <code>source config.env</code>, then run</td></tr>
<tr><td nowrap>See how a new AI differs before switching</td><td><code>python3 -I fetcher/check_ai.py --n 16</code></td></tr>
<tr><td nowrap>Add a person</td><td>Add an entry under <code>people</code> in <code>people.json</code>, then <code>python3 -I fetcher/leaders.py --only new_key --backfill</code></td></tr>
<tr><td nowrap>I only changed a name or title</td><td><code>python3 -I fetcher/leaders.py --page-only</code> (no search, no AI)</td></tr>
<tr><td nowrap>Link to one person / the last 24 hours</td><td>Append <code>#who=jensen</code> / <code>#24h</code> to the URL; they combine: <code>#24h&who=jensen</code></td></tr>
<tr><td nowrap>Update automatically every 2 hours</td><td>Schedule it with crontab or GitHub Actions, see "Deploying"</td></tr>
<tr><td nowrap>Use the data in my own frontend</td><td>Read <code>site/data/leaders.json</code>, format under "Page data format"</td></tr>
</table>

## How It Works

```
people.json (the list + name-matching rules + recognized channels)
        │
        ▼
① Two YouTube searches per person: full name in quotes, full name + interview; this week, 20+ minutes
② A candidate needs the person's name in the title or description (or a title like "Nvidia CEO" in the title)
③ AI judging: is the person actually speaking; also a Chinese title, a one-line summary, duplicate removal   ← swappable, optional
④ Open the video page only for videos going on the site, to get the exact publish time and length
        │
        ▼
data/store.json (archive: judged once, kept 400 days)
        │
        ▼
site/data/leaders.json (page data: latest 20 per person)
        │
        ▼
site/index.html (Chinese) · site/en/index.html (English)
```

- **Search, judge, then open pages**: a search page shows many results at once but only an approximate time ("5 hours ago"); a video page has the exact time, but open too many and YouTube asks for a bot check (in testing, opening 60+ in a row triggered it). So only videos that will be shown get their page opened; the rest are shown with the approximate time, marked "about" (约 on the Chinese site).
- **The archive accumulates**: search only returns recent videos, so history lives in the archive. New candidates are added, older videos that turn up again in search get their view counts updated, and anything older than 400 days is dropped.
- **Writes can't corrupt files**: the archive and page data are written to a temporary file and then renamed, so an interruption never leaves half a file. An unreadable archive (say, after a bad manual edit) isn't overwritten; it's moved aside as `store.json.bad-<time>` and the run starts from an empty archive.
- **One bad record doesn't sink the run**: records with wrong fields are dropped when read. People removed from the list keep their records in the archive (they come back if re-added); they're just not judged or shown.
- **Upcoming premieres and live streams** are skipped until they've aired, then picked up; videos the page reveals to be under 20 minutes are dropped.
- **One video, two people** (say, two leaders on the same stage): each gets judged separately and it appears under both.

## Data Sources

<table>
<tr><th nowrap>Source</th><th>What it provides</th><th nowrap>Key needed</th></tr>
<tr><td nowrap>YouTube video page</td><td>Exact publish time, length, full description, channel and channel ID, views</td><td nowrap>No</td></tr>
<tr><td nowrap>YouTube search page</td><td>Candidates: title, channel, verified badge, approximate time, length, views, snippet</td><td nowrap>No</td></tr>
<tr><td nowrap>AI (optional)</td><td>Whether the person is speaking, type, Chinese title, one-line summary, duplicates</td><td nowrap>Depends on provider</td></tr>
<tr><td nowrap>Channels recognized in <code>people.json</code></td><td>Which videos are shown when the AI is off or failed</td><td nowrap>—</td></tr>
<tr><td nowrap>YouTube images (<code>i.ytimg.com</code>)</td><td>Thumbnails on the site, loaded directly by the visitor's browser, never by the fetcher</td><td nowrap>No</td></tr>
</table>

What wins:

- **Time and length** come from the video page; the search page's values are placeholders, marked "about" on the site.
- **Whether a video is shown** is the AI's call; only unjudged videos fall back to the recognized official channels and interview shows.
- **View counts** are updated every time a video turns up in search, and again when its page is opened.

The fetcher only reads public YouTube pages: no login, no cookies, no bot-check bypassing, and it stops when rate-limited.

## Deploying

The site is fully static: put the whole `site/` folder on any static host (Cloudflare Workers / Pages, GitHub Pages, Netlify, your own server).

1. **Use your own domain**: both pages (`site/index.html`, `site/en/index.html`) reference `ceotalks.online`. When deploying elsewhere, replace the domain in `canonical`, `hreflang`, `og:url`, `og:image` and the footer. The share images print the domain too: edit that line in `brand/og.html` and `brand/og-en.html`, then rerun `zsh brand/make_images.sh`.
2. **Schedule the fetcher**: pick one of the two options below. The page shows the last update time and flags it once it's more than 8 hours old.

**Option 1: your own machine (crontab)**. Run it on a machine that can reach YouTube, then upload `site/data/leaders.json` to your host. For example, a crontab entry that runs every 2 hours:

```
25 */2 * * * cd /path/to/ceotalks && mkdir -p data && . ./config.env && python3 -I fetcher/leaders.py >> data/run.log 2>&1
```

Only one round runs at a time (file lock); if the previous round hasn't finished, the new one is skipped.

**Option 2: GitHub Actions + Cloudflare (what ceotalks.online uses)**. `.github/workflows/update-site.yml` runs a round every 2 hours: load the archive → fetch → AI judging → save the archive → upload `site/` to Cloudflare Workers (deploy settings are in `deploy/`). The archive lives on this repo's `data` branch as a single commit that each round overwrites. Set these under Settings → Secrets and variables → Actions:

<table>
<tr><th nowrap>Name</th><th nowrap>Where</th><th>What</th></tr>
<tr><td nowrap><code>LEADERS_AI_URL</code></td><td nowrap>Variables</td><td>AI endpoint, any OpenAI-compatible API, ending in <code>/chat/completions</code></td></tr>
<tr><td nowrap><code>LEADERS_AI_MODEL</code></td><td nowrap>Variables</td><td>Model name</td></tr>
<tr><td nowrap><code>LEADERS_AI_KEY</code></td><td nowrap>Secrets</td><td>The key for that API</td></tr>
<tr><td nowrap><code>CLOUDFLARE_API_TOKEN</code></td><td nowrap>Secrets</td><td>Cloudflare token: create it from the "Edit Cloudflare Workers" template; with your own domain, also add Zone → DNS → Edit; limit it to your own account and domain</td></tr>
<tr><td nowrap><code>CLOUDFLARE_ACCOUNT_ID</code></td><td nowrap>Variables</td><td>Your Cloudflare account ID</td></tr>
</table>

If any of the three AI settings is missing, that round skips the AI (and follows the "AI off" rules); if either Cloudflare setting is missing, it doesn't upload. Keys and tokens go in Secrets and never into code or logs. To use it from a fork, change the repository name in the workflow's `jobs.update.if` and the name and domain in `deploy/wrangler.jsonc`. You can also run "更新网站" (Update site) by hand from the Actions page, with options to fetch only some people, search this year, turn the AI off, skip saving, or skip uploading.

GitHub's machines hit YouTube's bot check on the very first video page (tested 2026-10), so this route sets `LEADERS_MAX_PAGES=0`: no video pages are opened, upload times are estimated from "x hours ago" on the search page and marked "about", and the AI only sees the short snippet from the search page. For exact times, use Option 1. Actions are free on public repos; private repos get 2,000 free minutes a month, and a round takes about 3 minutes, so every 2 hours fits but hourly would not.

## Page Data Format

You can also feed `site/data/leaders.json` into your own frontend:

```jsonc
{
  "meta": { "built": "2026-10-27T15:22:10Z", "ai": true, "aiProvider": "command", "errors": [], "rule": "…" },
  "people": [{
    "key": "jensen", "zh": "黄仁勋", "en": "Jensen Huang", "role": "英伟达 CEO", "role_en": "NVIDIA CEO",
    "searched": "2026-10-27T15:20:41Z",
    "videos": [{
      "id": "v-NGxyPjcrE", "url": "https://www.youtube.com/watch?v=v-NGxyPjcrE",
      "title": "NVIDIA GTC Berlin 2026 Keynote With CEO Jensen Huang",
      "zh": "英伟达 GTC 柏林 2026 主题演讲（CEO 黄仁勋）", "gist": "one-line summary (Chinese)",
      "kind": "演讲", "channel": "NVIDIA", "published": "2026-10-23T08:43:07Z", "approx": false,
      "duration": 5519, "views": 18910335, "judged": true
    }]
  }]
}
```

<table>
<tr><th nowrap>Field</th><th>Meaning</th></tr>
<tr><td nowrap><code>meta.built</code></td><td>Which run produced this data (UTC)</td></tr>
<tr><td nowrap><code>meta.ai</code></td><td>Whether the AI worked this run: <code>true</code> yes, <code>false</code> failed, <code>null</code> not called (off, or nothing to judge)</td></tr>
<tr><td nowrap><code>meta.errors</code></td><td>Problems this run (incomplete fetch, rate limits, AI failures, etc.), at most 10</td></tr>
<tr><td nowrap><code>searched</code></td><td>When this person was last searched successfully</td></tr>
<tr><td nowrap><code>approx</code></td><td><code>true</code>: the publish time is the search page's approximation, or the video page only gave a date</td></tr>
<tr><td nowrap><code>judged</code></td><td><code>false</code>: not judged by the AI (with AI off, videos from recognized channels are shown first)</td></tr>
<tr><td nowrap><code>kind</code></td><td>Stored in Chinese: 播客 / 访谈 / 演讲 / 座谈, shown on the English site as Podcast / Interview / Talk / Panel; it can also be 其他 (other) or empty, which the site doesn't display</td></tr>
<tr><td nowrap><code>duration</code></td><td>Seconds</td></tr>
</table>

## Project Structure

```
ceotalks/
├── fetcher/                 Fetcher (Python 3.9 standard library)
│   ├── leaders.py           Main program: search → match names → AI judge → open video pages → write archive → page data
│   ├── youtube.py           Reads YouTube search and video pages, detects rate limits and bot checks, proxy settings
│   ├── judge.py             AI judging: three providers, the prompt, parsing replies, duplicates
│   ├── people.py            Loads the list, matches names
│   ├── people.json          The list + name-matching rules + recognized channels
│   ├── check_ai.py          Compare judgments before switching AI (doesn't change the archive)
│   └── file_lock.py         One round at a time
├── site/                    The website (static)
│   ├── index.html           Chinese version
│   ├── en/index.html        English version
│   ├── app.js · style.css   Shared by both versions
│   ├── favicon.svg
│   ├── brand/               Logo, share images, app icons
│   └── data/leaders.json    Page data (created by the fetcher, not committed)
├── brand/                   Sources for the logo and share images
│   ├── make_logo.py         Draws the logo
│   ├── make_images.sh       Renders the share images and app icons
│   └── og.html · og-en.html · touch.html   Layouts for the share images and app icon
├── deploy/                  Cloudflare Workers deploy settings (wrangler.jsonc + worker.js that redirects www)
├── .github/workflows/update-site.yml   GitHub Actions: fetch, save and upload every 2 hours
├── assets/screenshots/      Screenshots used in the README
├── dev/serve.mjs            Tiny local preview server
├── tests/test_offline.py    14 offline tests
├── config.example.env       Example settings
├── README.md · README_en.md · CHANGELOG.md · LICENSE
└── data/                    Archive (created by the fetcher, not committed)
```

## Development and Tests

Offline, 14 tests: name matching (full name and surname, first names needing context, when titles count), the reply formats the AI parser accepts, the duplicate rules, saving unreadable replies, the OpenAI-compatible and local-command providers, the answer-length setting, keys never appearing in errors, local models without a key, what bad settings report, what's shown with AI off, and that every person has both Chinese and English titles.

```bash
python3 -I tests/test_offline.py
```

After changing the judging rules (the prompt in `judge.py`), bump `AI_VERSION` in the same file; the next round re-judges the whole archive under the new rules.

## FAQ

**Q: Very few videos show up?**
With AI off, only recognized official channels and interview shows are shown, which is a lot less. Turn on AI (see "AI Judging"), or add `--backfill` on the first run.

**Q: The log says "incomplete" or "bot check"?**
YouTube occasionally returns an abnormal page; the round records it as incomplete, the page shows it, and the next round searches again. On a 429 or a bot check the round makes no more YouTube requests; don't rerun right away. The 30-page cap and 2-second spacing per round are there to avoid getting blocked.

**Q: Can it run on GitHub Actions or another cloud scheduler?**
Yes, the repo ships one (see Option 2 under "Deploying"). Search pages load fine, but video pages hit the bot check, so it doesn't open them and times are approximate. For exact times, run it on a home or office machine that can reach YouTube.

**Q: It can't connect at all?**
The machine needs to reach YouTube. The fetcher follows the system `HTTPS_PROXY` by default; set `LEADERS_NO_PROXY=1` to bypass the proxy.

**Q: Why not use the official YouTube Data API?**
That needs an API key and has a daily quota. Reading public pages needs nothing; the trade-off is that `youtube.py` has to be updated when YouTube changes its page structure.

**Q: Will a different AI judge differently?**
Somewhat. Run `check_ai.py` on a sample first to see how far it is from the archive.

**Q: Something was judged wrong?**
Judged videos are never judged again, and there's no command yet to override a single verdict. While the fetcher isn't running, back up `data/store.json`, set that video's `keep` to `true` or `false`, then run `--page-only` to rewrite the page data. If judging is too loose or too strict overall, edit the prompt in `judge.py` and bump `AI_VERSION`; the next round re-judges everything.

**Q: Why only 20 minutes and up?**
Short videos are mostly clips and cuts. Podcasts, interviews and talks with the person themselves are almost always over 20 minutes.

**Q: Can it cover other platforms (Bilibili, X, podcast apps)?**
YouTube only, for now.

## Changelog

See [CHANGELOG.md](CHANGELOG.md). v1.0.0 (2026-10-28) is the first release.

## Disclaimer

- This project is not affiliated with YouTube, Google, or any person or company on the list.
- Videos belong to their creators. The site shows only titles, channel names, thumbnails and links; watch the videos on YouTube.
- Chinese titles and one-line summaries are AI-generated from the original title and description and may be wrong; the original video is authoritative.
- The fetcher reads public YouTube pages. Follow YouTube's Terms of Service and keep the request rate low.
- The site only organizes videos and is not investment advice.

## License

[Apache License 2.0](LICENSE)

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
