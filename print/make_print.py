"""Printable posters and wallet cards with real QR codes.

  python3 make_print.py                      -> QR codes point to https://helpnearyou.org
  python3 make_print.py https://other.address

Writes:
  poster-letter.pdf      8.5x11 poster with 8 tear-off tabs (each tab has its own QR)
  poster-letter-notabs.pdf   same poster, no tabs (for frames, bulletin boards, glass doors)
  poster-restroom.pdf    half-letter (5.5x8.5) poster for inside restroom stalls: crisis and safety first
  wallet-cards.pdf       2 pages: 10 fronts, then 10 backs, on Avery 5371/8371-style business card sheets
                         (or plain card stock, cut on the marks). Print double-sided, flip on long edge.
"""
import os, sys, subprocess, base64
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "..", "vendor")
# The QR opens the app with a "Save it to your phone" box (#install). Change this one line when the domain is bought.
SITE = sys.argv[1] if len(sys.argv) > 1 else "https://hny191.github.io/helpnearyou/"
URL = SITE.rstrip("/") + "/#install"
SHOW = SITE.replace("https://", "").replace("http://", "").rstrip("/")

def qr(url, ec="Q"):
    return subprocess.run(["node", "/tmp/npmv/qr.js", url, ec], capture_output=True, text=True, check=True).stdout

def font(k): return base64.b64encode(open(os.path.join(VENDOR, f"ah-{k}.woff2"), "rb").read()).decode()
FONTS = f"""@font-face{{font-family:AH;font-weight:400;src:url(data:font/woff2;base64,{font('400')}) format('woff2')}}
@font-face{{font-family:AH;font-weight:700;src:url(data:font/woff2;base64,{font('700')}) format('woff2')}}"""
def ico(path, color, size, sw=2.2):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" style="color:{color}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
PIN = '<path d="M3.5 12.5C3.7 16.9 6.9 20 10.55 20.4"/><path d="M13.45 20.4C17.1 20 20.3 16.9 20.5 12.5"/><path d="M3.5 12.5c1.6 0 2.6.9 3.4 2.2M20.5 12.5c-1.6 0-2.6.9-3.4 2.2"/><path d="M12 14.8C11.2 14 7.6 11.4 7.8 9.3C8 6.8 11.2 6.4 12 8.9C12.8 6.4 16 6.8 16.2 9.3C16.4 11.4 12.8 14 12 14.8Z" fill="currentColor" stroke="none"/>'
ITEMS = [("Food &amp; meals", "#8A5300", '<path d="M4 11h16a8 8 0 0 1-16 0z"/><path d="M12 3v4M8.5 5v2M15.5 5v2"/>'),
         ("A place to stay", "#1E4FB8", '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>'),
         ("Health care", "#1B6B3A", '<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M12 8v8M8 12h8"/>'),
         ("Heating help", "#A5401A", '<path d="M12 21a6 6 0 0 0 6-6c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-3-2 2-3 4-3 7a6 6 0 0 0 6 6z"/>'),
         ("Bus fare &amp; rides", "#1F6670", '<rect x="5" y="3" width="14" height="15" rx="3"/><path d="M5 11h14M8 21l1.5-3M16 21l-1.5-3"/>'),
         ("Replace your ID", "#3D4652", '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="12" r="2.5"/><path d="M14 10h4M14 14h4"/>'),
         ("Talk to someone", "#5B3A9E", '<path d="M4 5h16v11H9l-5 4z"/>'),
         ("Legal help", "#5C5137", '<path d="M12 4v16M7 20h10M5 8h14"/><path d="M5 8l-2.5 6a3 3 0 0 0 5 0zM19 8l-2.5 6a3 3 0 0 0 5 0z"/>')]
BIG, SMALL = qr(URL, "Q"), qr(URL, "M")
BASE = "*{box-sizing:border-box}html,body{margin:0;padding:0}body{font-family:AH,sans-serif;color:#17202A;-webkit-print-color-adjust:exact;print-color-adjust:exact}.q svg{display:block;width:100%;height:100%}"

def poster(tabs=True):
    items = "".join(f'<span style="display:flex;align-items:center;gap:.14in">{ico(p, c, 30)}{t}</span>' for t, c, p in ITEMS)
    tab = f'''<div style="border-right:2px dashed #8A96A6;display:flex;flex-direction:column;align-items:center;gap:.08in;padding:.12in 0 0">
      <div class="q" style="width:.62in;height:.62in">{SMALL}</div>
      <span style="writing-mode:vertical-rl;transform:rotate(180deg);font-size:12px;font-weight:700;line-height:1.15;text-align:center">{SHOW.replace("/", "<br>/", 1)}<br><span style="font-weight:400">or call 211</span></span></div>'''
    tabrow = f'<div style="margin-top:auto;border-top:2px dashed #8A96A6;display:grid;grid-template-columns:repeat(8,1fr);height:2.05in">{tab*8}</div>' if tabs else \
             f'<div style="margin:auto .58in .5in;font-size:15px;color:#3D4652">Information guide, not an emergency service. In danger? Call 911. · Places and hours are checked every night; call ahead if you can.</div>'
    return f'''<div style="width:8.5in;height:11in;display:flex;flex-direction:column;overflow:hidden">
  <div style="background:#1E4FB8;color:#fff;padding:.46in .58in .38in;display:flex;flex-direction:column;gap:.12in">
    <div style="display:flex;align-items:center;gap:10px;font-size:20px;font-weight:700;color:#DCE6FB">{ico(PIN,"#fff",26)}Help Near You</div>
    <div style="font-size:92px;font-weight:700;line-height:.98;letter-spacing:-1.5px">Free help<br>near you.</div>
    <span style="font-size:28px;color:#DCE6FB">Ayuda gratis cerca de ti</span></div>
  <div style="padding:.34in .58in 0;display:flex;gap:.38in;align-items:center">
    <div style="flex:1;display:grid;grid-template-columns:1fr 1fr;gap:.17in .2in;font-size:21px;font-weight:700;white-space:nowrap">{items}
      <span style="grid-column:span 2;font-size:19px;font-weight:400;color:#3D4652;white-space:normal">and more: phones, showers, jobs, benefits, women's health</span></div>
    <div style="display:flex;flex-direction:column;align-items:center;gap:.08in;flex-shrink:0">
      <div class="q" style="width:2.35in;height:2.35in;padding:.12in;border:3px solid #17202A;border-radius:14px;background:#fff">{BIG}</div>
      <span style="font-size:20px;font-weight:700">Scan for the free app</span>
      <span style="font-size:15px;font-weight:700;color:#163C8C">{SHOW}</span></div></div>
  <div style="margin:.27in .58in 0;padding:.14in .2in;border-radius:14px;background:#EEF3FD;font-size:19px;display:flex;gap:18px;flex-wrap:wrap;color:#163C8C;font-weight:700">
    <span>Free</span><span>·</span><span>No sign-up</span><span>·</span><span>Nothing is tracked</span><span>·</span><span>Works with no signal</span></div>
  <div style="margin:.2in .58in 0;display:grid;grid-template-columns:1fr 1fr;gap:.17in">
    <div style="padding:.14in .19in;border-radius:14px;border:2px solid #17202A;display:flex;flex-direction:column"><span style="font-size:17px;color:#3D4652">No smartphone?</span><span style="font-size:24px;font-weight:700">Call 211, any hour</span></div>
    <div style="padding:.14in .19in;border-radius:14px;background:#8A1C3F;color:#fff;display:flex;flex-direction:column"><span style="font-size:17px;color:#FBE3EB">Need to talk right now?</span><span style="font-size:24px;font-weight:700">Call or text 988</span></div></div>
  {tabrow}</div>'''

def restroom():
    return f'''<div style="width:5.5in;height:8.5in;padding:.4in;display:flex;flex-direction:column;gap:.2in;overflow:hidden;justify-content:space-between">
  <div style="display:flex;align-items:center;gap:8px;font-size:15px;font-weight:700;color:#1E4FB8">{ico(PIN,"#1E4FB8",20)}Help Near You</div>
  <div style="font-size:46px;font-weight:700;line-height:1.02">You're not alone.<br>Help is free.</div>
  <div style="padding:.14in .18in;border-radius:12px;background:#8A1C3F;color:#fff"><div style="font-size:15px;color:#FBE3EB">Thinking about ending your life, or need to talk?</div><div style="font-size:26px;font-weight:700">Call or text 988</div><div style="font-size:14px">Or text HOME to 741741. Free, 24/7.</div></div>
  <div style="padding:.14in .18in;border-radius:12px;background:#6E2C6E;color:#fff"><div style="font-size:15px;color:#F4E6F4">Someone hurting you at home?</div><div style="font-size:22px;font-weight:700">1-800-799-7233</div><div style="font-size:14px">Or text START to 88788. Free, private, 24/7.</div></div>
  <div style="padding:.12in .18in;border-radius:12px;border:2px solid #17202A;font-size:15px"><b style="font-size:20px">Call 211</b> for food, a place to stay, heat help and more, any hour.</div>
  <div style="display:flex;gap:.2in;align-items:center">
    <div class="q" style="width:1.9in;height:1.9in;padding:.07in;border:2px solid #17202A;border-radius:10px;flex-shrink:0">{BIG}</div>
    <div style="font-size:15px"><b style="font-size:17px">Scan for the free app</b><br>Food, shelter, clinics, someone to talk to. Nothing is tracked.<br><b style="color:#163C8C">{SHOW}</b></div></div>
  <div style="font-size:12px;color:#3D4652">In danger right now? Call 911. Can't talk? Try texting 911.</div></div>'''

def card_front():
    return f'''<div style="width:3.5in;height:2in;background:#1E4FB8;color:#fff;padding:.16in .16in .16in .19in;display:flex;align-items:center;gap:.14in;overflow:hidden">
  <div style="display:flex;flex-direction:column;gap:5px;flex:1">
    <span style="display:flex;align-items:center;gap:6px;font-size:12px;font-weight:700;color:#DCE6FB">{ico(PIN,"#fff",14,2.4)}Help Near You</span>
    <span style="font-size:25px;font-weight:700;line-height:1.05">Free help<br>near you.</span>
    <span style="font-size:11.5px;line-height:1.3;color:#E2ECFF">Food, shelter, clinics, heat help, bus fare. Open now, on your phone.</span>
    <span style="font-size:10.5px;font-weight:700">{SHOW}</span></div>
  <div class="q" style="width:1.12in;height:1.12in;padding:.06in;background:#fff;border-radius:8px;flex-shrink:0">{SMALL}</div></div>'''

def card_back():
    row = lambda a, b, big=False: f'<div style="display:flex;justify-content:space-between;align-items:baseline;padding:3px 10px;border-bottom:1px solid #ECEFF3"><span style="font-size:12.5px;color:#3D4652">{a}</span><span style="font-size:15px;font-weight:700">{b}</span></div>'
    return f'''<div style="width:3.5in;height:2in;background:#fff;padding:.13in .17in;display:flex;flex-direction:column;gap:4px;overflow:hidden">
  <div style="display:flex;justify-content:space-between;align-items:baseline;padding:5px 10px;border-radius:8px;background:#8A1C3F;color:#fff"><span style="font-size:13px">Need to talk?</span><span style="font-size:17px;font-weight:700">Call or text 988</span></div>
  {row("Rather text?","HOME to 741741")}{row("Local help, any hour","Call 211")}{row("Emergency","911")}
  <div style="display:flex;align-items:flex-end;gap:6px;padding:3px 10px 0;font-size:12px;color:#3D4652"><span>My place:</span><span style="flex:1;border-bottom:1px solid #8A96A6;height:14px"></span></div>
  <span style="margin-top:auto;padding:0 10px;font-size:11.5px;color:#4A5562">Free · no sign-up · nothing tracked</span></div>'''

def card_sheet(fn, mirror):
    # Avery 5371/8371 layout: 2 across x 5 down, 3.5x2in, top margin 0.5in, side margin 0.75in, no gaps.
    cells = []
    for r in range(5):
        for c in range(2):
            x = 0.75 + (3.5 * ((1 - c) if mirror else c))
            cells.append(f'<div style="position:absolute;left:{x}in;top:{0.5 + 2*r}in">{fn()}</div>')
    marks = "".join(f'<div style="position:absolute;left:{x}in;top:0;width:0;height:.35in;border-left:.5px solid #999"></div><div style="position:absolute;left:{x}in;bottom:0;width:0;height:.35in;border-left:.5px solid #999"></div>' for x in (0.75, 4.25, 7.75)) \
          + "".join(f'<div style="position:absolute;top:{y}in;left:0;height:0;width:.6in;border-top:.5px solid #999"></div><div style="position:absolute;top:{y}in;right:0;height:0;width:.6in;border-top:.5px solid #999"></div>' for y in (0.5, 2.5, 4.5, 6.5, 8.5, 10.5))
    return f'<div style="position:relative;width:8.5in;height:11in;overflow:hidden;page-break-after:always">{"".join(cells)}{marks}</div>'

def pdf(name, body, w, h):
    html = f"<!doctype html><html><head><meta charset=utf-8><style>{FONTS}{BASE}@page{{size:{w} {h};margin:0}}</style></head><body>{body}</body></html>"
    open(os.path.join(HERE, name.replace(".pdf", ".html")), "w").write(html)
    pg.set_content(html); pg.wait_for_timeout(300)
    pg.pdf(path=os.path.join(HERE, name), width=w, height=h, print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pdf("poster-letter.pdf", poster(True), "8.5in", "11in")
    pdf("poster-letter-notabs.pdf", poster(False), "8.5in", "11in")
    pdf("poster-restroom.pdf", restroom(), "5.5in", "8.5in")
    pdf("wallet-cards.pdf", card_sheet(card_front, False) + card_sheet(card_back, True), "8.5in", "11in")
    # previews to look at
    for n, w, h in (("poster-letter", 816, 1056), ("poster-restroom", 528, 816), ("wallet-cards", 816, 1056)):
        pg.set_viewport_size({"width": w, "height": h}); pg.goto("file://" + os.path.join(HERE, n + ".html")); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(HERE, n + "-preview.png"))
    b.close()
print("QR codes point to", URL)
