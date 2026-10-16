"""Help Near You updater. Runs by itself twice a day on GitHub, early morning and night (see .github/workflows/update.yml).

What it does, in order:
  1. Applies corrections in corrections/*.json (from phone calls and checked reports). These are the only way
     listing details change: nothing is changed just because a web page changed.
  2. Checks every listing's web page. If a page is gone two checks in a row, or its text changed since the last check,
     the listing goes on the to-check list (status/to-check.md), so a person can call and confirm.
  3. Marks listings as "not confirmed recently" once they haven't been checked for 6 months (the app then shows
     "call first"), and low after a year.
  4. Rebuilds the site (build.py).

Run by hand:  python3 update.py            (everything)
              python3 update.py --no-web   (skip the web checks, e.g. offline)
"""
import json, os, re, sys, glob, hashlib, datetime, urllib.request, urllib.error, concurrent.futures, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")
STATE = os.path.join(HERE, "state")
STATUS = os.path.join(HERE, "status")
os.makedirs(STATE, exist_ok=True); os.makedirs(STATUS, exist_ok=True)
TODAY = datetime.date.today()
data = json.load(open(DATA, encoding="utf-8"))
L = data["listings"]
byid = {x["id"]: x for x in L}
log = []

# ---------- 1. corrections ----------
# corrections/<anything>.json = a list of
#   {"id": "listing-id", "set": {"hours": {...}, "hours_text": "...", "phone": "..."}, "checked": "2026-10-20", "how": "called, spoke to Mary"}
#   {"id": "listing-id", "remove": true, "how": "closed in 2025, per the church office"}
#   {"add": {full listing}, "how": "found on a call"}
applied_file = os.path.join(STATE, "applied.json")
applied = set(json.load(open(applied_file))) if os.path.exists(applied_file) else set()
for f in sorted(glob.glob(os.path.join(HERE, "corrections", "*.json"))):
    for i, c in enumerate(json.load(open(f, encoding="utf-8"))):
        key = f"{os.path.basename(f)}#{i}"
        if key in applied: continue
        if c.get("add"):
            x = c["add"]; x.setdefault("checked", c.get("checked", TODAY.isoformat())); x.setdefault("cats", [x.pop("category", "food")])
            if x["id"] in byid: log.append(f"- skipped add (id exists): {x['id']}"); continue
            L.append(x); byid[x["id"]] = x; log.append(f"- added **{x['name']}** ({c.get('how','')})")
        elif c.get("remove"):
            x = byid.pop(c["id"], None)
            if x: L.remove(x); log.append(f"- removed **{x['name']}** ({c.get('how','')})")
            else: log.append(f"- remove: no listing {c['id']}")
        else:
            x = byid.get(c.get("id"))
            if not x: log.append(f"- correction: no listing {c.get('id')}"); continue
            x.update(c.get("set", {}))
            x["checked"] = c.get("checked", TODAY.isoformat())
            x["confirmed"] = x["checked"]          # a person confirmed it (phone call or the place's own page)
            if c.get("confirmed", True): x["confidence"] = "high"
            if c.get("how"): x["notes"] = ((x.get("notes") or "") + f" Confirmed by phone {x['checked']}: {c['how']}.").strip()
            log.append(f"- updated **{x['name']}**: {', '.join(c.get('set', {})) or 'confirmed as is'}")
        applied.add(key)
json.dump(sorted(applied), open(applied_file, "w"), indent=0)

# ---------- 2. web checks ----------
def page_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "HelpNearYou-checker/1.0 (+https://helpnearyou.org; twice-daily link check)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read(1_500_000).decode("utf-8", "ignore")
    raw = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", raw)
    txt = re.sub(r"<[^>]+>", " ", raw)
    txt = re.sub(r"\s+", " ", txt)
    # ignore things that change every load: dates, times of day, counters
    txt = re.sub(r"\b\d{1,2}:\d\d(:\d\d)?\b|\b(19|20)\d\d\b|\b\d{5,}\b", "", txt)
    return txt

checks_file = os.path.join(STATE, "pages.json")
checks = json.load(open(checks_file)) if os.path.exists(checks_file) else {}
gone, changed = [], []
if "--no-web" not in sys.argv:
    urls = sorted({x.get("source_url") for x in L if (x.get("source_url") or "").startswith("http")})
    def one(u):
        try: return u, "ok", hashlib.sha1(page_text(u).encode()).hexdigest()
        except urllib.error.HTTPError as e: return u, ("gone" if e.code in (404, 410) else f"http {e.code}"), None
        except Exception as e: return u, "error", None
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        for u, st, h in ex.map(one, urls):
            prev = checks.get(u, {})
            rec = {"status": st, "hash": h or prev.get("hash"), "seen": TODAY.isoformat(), "misses": 0}
            if st == "gone":
                # only call it gone once it has been missing on two different days
                # (a run is triggered by every edit too, so two runs can be minutes apart)
                rec["first_miss"] = prev.get("first_miss") or TODAY.isoformat()
                rec["misses"] = prev.get("misses", 0) + 1
                if TODAY.isoformat() > rec["first_miss"] and not prev.get("reported"):
                    gone.append(u); rec["reported"] = True
                else:
                    rec["reported"] = prev.get("reported", False)
            elif st == "ok" and prev.get("hash") and h != prev["hash"]:
                changed.append(u)
            checks[u] = rec
    json.dump(checks, open(checks_file, "w"), indent=0)
    # a listing whose source page loaded fine and hasn't changed gets today's date as "source checked"
    for x in L:
        r = checks.get(x.get("source_url") or "")
        if r and r.get("status") == "ok" and r.get("seen") == TODAY.isoformat() and x.get("source_url") not in changed:
            x["page_seen"] = TODAY.isoformat()

# ---------- 3. age ----------
aged = []
for x in L:
    try: d = datetime.date.fromisoformat(str(x.get("checked"))[:10])
    except ValueError: continue
    age = (TODAY - d).days
    if age > 365 and x.get("confidence") != "low": x["confidence"] = "low"; aged.append(x)
    elif age > 182 and x.get("confidence") == "high": x["confidence"] = "medium"; aged.append(x)

# Problem reports are NOT pulled in here on purpose: people sometimes type personal details into a note,
# and this repository is public. Reports stay in the private Google Sheet behind the report form.

# ---------- write ----------
data["checked"] = max([data.get("checked", "")] + [str(x.get("checked", ""))[:10] for x in L])
data["built"] = TODAY.isoformat()
json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

url2 = {}
for x in L: url2.setdefault(x.get("source_url"), []).append(x)
out = [f"# To check ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} UTC)", "",
       "Call these places to confirm. When you do, add a correction (see corrections/README.md).", ""]
if log: out += ["## Applied this run"] + log + [""]
def rows(urls):
    seen, out_ = set(), []
    for u in urls:
        for x in url2.get(u, []):
            k = (x["name"], x.get("phone"))
            if k in seen: continue
            seen.add(k); out_.append(f"- [ ] **{x['name']}** · {x.get('phone') or 'no phone'} · {u}")
    return out_
if gone: out += ["## Web page gone on two different days: may have closed (or the site moved the page)"] + rows(gone) + [""]
if changed: out += ["## Web page changed since the last check: hours or details may have changed"] + rows(changed) + [""]
if aged: out += [f"## {len(aged)} listings now show 'call first' because they haven't been checked in 6+ months"] + [f"- {x['name']} (last checked {x.get('checked')})" for x in aged[:200]] + [""]
open(os.path.join(STATUS, "to-check.md"), "w").write("\n".join(out) + "\n")
print(f"corrections: {len(log)}, pages gone: {len(gone)}, changed: {len(changed)}, aged: {len(aged)}")

subprocess.run([sys.executable, os.path.join(HERE, "build.py")], check=True)
