"""Build Help Near You.

  python3 build.py            -> hny.html (the claude.ai preview) and site/ (the real website, ready to host)

site/ is everything helpnearyou.org needs: the app with today's data inside it, an offline worker,
an install manifest, icons, the QR library and the font (so nothing loads from other sites).
The updater (update.py, twice a day) calls this after it refreshes data.json.
"""
import json, os, shutil, hashlib, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "site")
VENDOR = os.path.join(HERE, "vendor")          # qrcode.js + font files, copied once from npm
CONFIG = os.path.join(HERE, "site_config.json")

tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
cfg = json.load(open(CONFIG)) if os.path.exists(CONFIG) else {}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

def fill(t, site):
    report = cfg.get("report", {}) if site else {}
    return (t.replace("__DATA__", blob)
             .replace("__SITE__", "true" if site else "false")
             .replace("__BUILD__", __import__("datetime").datetime.utcnow().strftime("%m%d-%H%M"))
             .replace("__REPORT__", json.dumps(report)))

# 1. the preview (one file, published as a claude.ai artifact)
open(os.path.join(HERE, "hny.html"), "w", encoding="utf-8").write(fill(tpl, False))

# 2. the website
HEAD_OLD = tpl[:tpl.index("<style>")]
HEAD_NEW = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Help Near You</title>
<meta name="description" content="Free help near you in New York: food, shelter, health care, crisis lines, benefits, heat help and more. Nothing to sign up for, nothing tracked.">
<meta name="theme-color" content="#1E4FB8">
<meta name="referrer" content="no-referrer">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icon-192.png">
<style>
@font-face{font-family:'Atkinson Hyperlegible';font-style:normal;font-weight:400;font-display:swap;src:url(fonts/ah-400.woff2) format('woff2')}
@font-face{font-family:'Atkinson Hyperlegible';font-style:normal;font-weight:700;font-display:swap;src:url(fonts/ah-700.woff2) format('woff2')}
@font-face{font-family:'Atkinson Hyperlegible';font-style:italic;font-weight:400;font-display:swap;src:url(fonts/ah-400i.woff2) format('woff2')}
body{margin:0}
</style>
<script src="qrcode.js"></script>
"""
page = HEAD_NEW + fill(tpl[len(HEAD_OLD):], True)
page += """
<script>
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js", {updateViaCache: "none"}).catch(()=>{});
</script>
</body>
</html>
"""
page = page.replace('<div class="wrap" id="app"></div>', '</head>\n<body>\n<div class="wrap" id="app"></div>', 1)
# the <style> block of the app sits before </head>: move </head><body> after it
page = page.replace("</style>\n\n</head>", "</style>\n</head>")

if os.path.exists(SITE): shutil.rmtree(SITE)
os.makedirs(os.path.join(SITE, "fonts"))
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(page)
shutil.copy(os.path.join(VENDOR, "qrcode.js"), SITE)
for k in ("400", "700", "400i"):
    shutil.copy(os.path.join(VENDOR, f"ah-{k}.woff2"), os.path.join(SITE, "fonts"))
shutil.copy(os.path.join(VENDOR, "OFL.txt"), os.path.join(SITE, "fonts"))
shutil.copy(os.path.join(HERE, "about.html"), SITE)
for f in ("icon.svg", "icon-192.png", "icon-512.png", "icon-maskable-512.png"):
    shutil.copy(os.path.join(VENDOR, f), SITE)

json.dump({
    "name": "Help Near You", "short_name": "Help Near You",
    "description": "Free help near you: food, shelter, health, crisis lines and more.",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#F7F6F2", "theme_color": "#1E4FB8",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
}, open(os.path.join(SITE, "manifest.webmanifest"), "w"), indent=1)

files = ["./", "index.html", "about.html", "qrcode.js", "manifest.webmanifest", "icon.svg", "icon-192.png", "icon-512.png",
         "fonts/ah-400.woff2", "fonts/ah-700.woff2", "fonts/ah-400i.woff2"]
ver = hashlib.sha1(page.encode()).hexdigest()[:10]
open(os.path.join(SITE, "sw.js"), "w").write(f"""// Help Near You offline worker. Keeps the app on the phone so it opens with no signal.
// It stores only the app's own files. Nothing anyone searches or taps is stored or sent.
const V = "hny-{ver}";
const FILES = {json.dumps(files)};
self.addEventListener("install", e => {{ e.waitUntil(caches.open(V).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); }});
self.addEventListener("activate", e => {{ e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); }});
self.addEventListener("fetch", e => {{
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;      // other sites: straight through, never stored
  if (e.request.mode === "navigate" || u.pathname.endsWith("/") || u.pathname.endsWith("index.html")) {{
    // the page: ask the server for the newest version (skipping the browser cache) for up to 3 s, else use the saved copy
    e.respondWith(Promise.race([fetch(e.request.url, {{cache: "no-cache", credentials: "same-origin"}}).then(r => {{ const c = r.clone(); caches.open(V).then(k => k.put("index.html", c)); return r; }}),
      new Promise((_, no) => setTimeout(no, 3000))]).catch(() => caches.match("index.html")));
    return;
  }}
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
}});
""")
open(os.path.join(SITE, "robots.txt"), "w").write("User-agent: *\nAllow: /\n")
if cfg.get("domain"):
    open(os.path.join(SITE, "CNAME"), "w").write(cfg["domain"] + "\n")
print("built hny.html and site/ :", len(data["listings"]), "listings,", os.path.getsize(os.path.join(SITE, "index.html")) // 1024, "KB page")
