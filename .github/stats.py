# Posts GoatCounter stats to a webhook (Discord or Slack).
# Env: GOATCOUNTER_TOKEN, WEBHOOK_URL, GC_SITE (e.g. burntpineapples), MODE:
#   (unset) yesterday's report | new = suggestions from the previous full hour | all = every suggestion ever
import json, os, sys, urllib.request
from datetime import date, datetime, timedelta, timezone

site, token, hook = os.environ.get("GC_SITE", "burntpineapples"), os.environ["GOATCOUNTER_TOKEN"], os.environ["WEBHOOK_URL"]
day = date.today() - timedelta(days=1)
q = f"start={day}T00:00:00Z&end={day}T23:59:59Z"  # date-only start/end makes stats/total 404

def api(path):
    req = urllib.request.Request(f"https://{site}.goatcounter.com/api/v0/{path}",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def post(msg):
    msg = msg[:1990]  # Discord caps messages at 2000 chars
    # allowed_mentions: visitor-typed suggestions can't ping @everyone
    body = json.dumps({"content": msg, "text": msg, "allowed_mentions": {"parse": []}}).encode()
    urllib.request.urlopen(urllib.request.Request(hook, body, {"Content-Type": "application/json", "User-Agent": "stats-bot"}), timeout=30)
    print(msg)

def suggestions(query):
    hits = api(f"stats/hits?{query}&limit=100").get("hits", [])
    return [(h.get("title") or h["path"].lstrip("/")[8:], h["count"]) for h in hits if h["path"].lstrip("/").startswith("suggest/")]

mode = os.environ.get("MODE", "")
if mode in ("new", "all"):
    hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    # ponytail: "previous full hour" window; a GitHub cron delayed past the next hour can skip or repeat one hour
    start = hour - timedelta(hours=1) if mode == "new" else datetime(2026, 11, 1, tzinfo=timezone.utc)
    end = hour - timedelta(seconds=1) if mode == "new" else hour + timedelta(hours=1)  # "all" includes this hour
    sugs = suggestions(f"start={start:%Y-%m-%dT%H:%M:%SZ}&end={end:%Y-%m-%dT%H:%M:%SZ}")
    if mode == "new" and not sugs: sys.exit(print("no new suggestions"))
    title = "💡 **New game suggestion" + ("s" if len(sugs) > 1 else "") + "**" if mode == "new" else f"💡 **All game suggestions ({len(sugs)})**"
    post("\n".join([title] + ([f"• {t[:150]}" + (f" (x{n})" if n > 1 else "") for t, n in sugs] or ["none yet"])))
    sys.exit()

def top(path, n=5):
    rows = api(f"stats/{path}?{q}&limit={n}").get("stats", [])
    return ", ".join(f"{r.get('name') or '(direct)'} {r['count']}" for r in rows[:n]) or "none"

try:
    total = api(f"stats/total?{q}")
    hits = api(f"stats/hits?{q}&limit=100").get("hits", [])
    plays = sorted((h for h in hits if h.get("event") and h["path"].lstrip("/").startswith("play/")), key=lambda h: -h["count"])
    sugs = [t for t, n in suggestions(q)]
    lines = [
        f"🍍 **Pineapple Arcade, {day:%a %b %d}**",
        f"Page views: **{total.get('total', 0)}**   Game plays: **{total.get('total_events', sum(h['count'] for h in plays))}**",
        "**Top games:** " + (", ".join(f"{h.get('title') or h['path'].lstrip('/')[5:]} ({h['count']})" for h in plays[:10]) or "none"),
        "**From:** " + top("toprefs"),
        "**Countries:** " + top("locations"),
        "**Browsers:** " + top("browsers"),
        "**💡 Suggestions:** " + ("\n• " + "\n• ".join(s[:150] for s in sugs[:20]) if sugs else "none"),
    ]
except Exception as e:
    lines = [f"🍍 Pineapple Arcade stats failed for {day}: {e}"]

post("\n".join(lines))
