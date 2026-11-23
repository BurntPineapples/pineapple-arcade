# Posts yesterday's GoatCounter stats to a webhook (Discord or Slack).
# Env: GOATCOUNTER_TOKEN, WEBHOOK_URL, GC_SITE (e.g. pineapplearcade)
import json, os, urllib.request
from datetime import date, timedelta

site, token, hook = os.environ.get("GC_SITE", "pineapplearcade"), os.environ["GOATCOUNTER_TOKEN"], os.environ["WEBHOOK_URL"]
day = date.today() - timedelta(days=1)
q = f"start={day}&end={day}"

def api(path):
    req = urllib.request.Request(f"https://{site}.goatcounter.com/api/v0/{path}",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def top(path, n=5):
    rows = api(f"stats/{path}?{q}&limit={n}").get("stats", [])
    return ", ".join(f"{r.get('name') or '(direct)'} {r['count']}" for r in rows[:n]) or "none"

try:
    total = api(f"stats/total?{q}")
    hits = api(f"stats/hits?{q}&limit=50").get("hits", [])
    plays = sorted((h for h in hits if h.get("event")), key=lambda h: -h["count"])
    lines = [
        f"🍍 **Pineapple Arcade, {day:%a %b %d}**",
        f"Page views: **{total.get('total', 0)}**   Game plays: **{total.get('total_events', sum(h['count'] for h in plays))}**",
        "**Top games:** " + (", ".join(f"{h.get('title') or h['path'][5:]} ({h['count']})" for h in plays[:10]) or "none"),
        "**From:** " + top("toprefs"),
        "**Countries:** " + top("locations"),
        "**Browsers:** " + top("browsers"),
    ]
except Exception as e:
    lines = [f"🍍 Pineapple Arcade stats failed for {day}: {e}"]

msg = "\n".join(lines)
body = json.dumps({"content": msg, "text": msg}).encode()
urllib.request.urlopen(urllib.request.Request(hook, body, {"Content-Type": "application/json", "User-Agent": "stats-bot"}), timeout=30)
print(msg)
