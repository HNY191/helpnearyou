# Putting Help Near You online

## 1. GitHub Pages (free)
1. On this repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. **Actions** tab → "Twice-daily update" → **Run workflow**. (If Actions asks to be enabled, enable it.)
3. In a few minutes the site is live at `https://[YOUR-USERNAME].github.io/helpnearyou/`.
   It then updates itself twice a day.

## 2. The domain (helpnearyou.org)
1. Buy `helpnearyou.org` from any domain seller (Cloudflare, Porkbun and Namecheap are cheap; about $10-15 a year).
2. Here: **Settings → Pages → Custom domain** → `helpnearyou.org` → Save. Tick **Enforce HTTPS** once it's offered.
3. At the domain seller, add the DNS records GitHub shows. For a root domain that's four `A` records:
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`,
   plus a `CNAME` record for `www` pointing to `[YOUR-USERNAME].github.io`.
4. In `site_config.json` set `"domain": "helpnearyou.org"` and commit. (This keeps the domain set after each update.)
5. Wait up to a day for it to switch over. Only print the posters after `https://helpnearyou.org` opens the app.

## 3. Problem reports (Google Form)
1. Make a Google Form with 7 **short answer** questions named exactly: listing, name, county, issue, note, day, version.
2. ⋮ menu → **Get pre-filled link** → type anything in each box → **Get link** → copy it.
   Each question has a number like `entry.123456789`.
3. In `site_config.json`:
   ```json
   "report": {
     "form": "https://docs.google.com/forms/d/e/<FORM ID>/formResponse",
     "fields": {"listing": "entry.…", "name": "entry.…", "county": "entry.…", "issue": "entry.…",
                "note": "entry.…", "day": "entry.…", "version": "entry.…"},
     "email": ""
   }
   ```
   (Use the form's address with `/viewform` changed to `/formResponse`.)
4. Keep the form's responses **private**. People sometimes type personal things into a note.

## 4. Keeping it current
- Phone-call results go in `corrections/` (see its README). Claude can write those files from the call vault.
- `status/to-check.md` lists places whose web pages changed or vanished. Call them, then add a correction.
