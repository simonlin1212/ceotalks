#!/bin/zsh
# 用本机 Chrome（无界面）把 og.html、og-en.html、touch.html 截成 PNG，放进 site/brand/。改了标志先跑 make_logo.py 再跑这个。
set -e
here=${0:A:h}
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
profile=$(mktemp -d)
trap 'rm -rf "$profile"' EXIT
shot() { "$chrome" --headless=new --disable-gpu --hide-scrollbars --no-first-run --user-data-dir="$profile" \
  --window-size="$2" --screenshot="$here/../site/brand/$3" "file://$here/$1" 2>/dev/null; }
shot og.html 1200,630 og.png
shot og-en.html 1200,630 og-en.png
shot touch.html 180,180 apple-touch-icon.png
echo "写好 site/brand/og.png、site/brand/og-en.png、site/brand/apple-touch-icon.png"
