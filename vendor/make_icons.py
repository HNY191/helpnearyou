"""Render the app icons (PNG) from icon.svg and icon-maskable.svg. Needs Playwright with Chromium."""
import os
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
svg, mask = open(os.path.join(D, "icon.svg")).read(), open(os.path.join(D, "icon-maskable.svg")).read()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    for name, s, size in (("icon-512.png", svg, 512), ("icon-192.png", svg, 192), ("icon-maskable-512.png", mask, 512)):
        pg.set_viewport_size({"width": size, "height": size})
        pg.set_content('<html><body style="margin:0;background:transparent">' + s.replace("<svg ", f'<svg width="{size}" height="{size}" ', 1) + "</body></html>")
        pg.screenshot(path=os.path.join(D, name), omit_background=True)
    b.close()
print("icons written")
