# indian-tender-scraper

Scrapes active government tenders from ~90 Indian NIC eProcurement portals
(CPPP, Defence, PSUs, PMGSY, and state portals) into CSV, with an optional
Flask UI and a second pass that pulls full tender details + PDFs.

## Files

| File | What it does |
|------|--------------|
| `sites.py` | List of portal names + base URLs. |
| `main.py` | Fetches each portal's "Latest Active Tenders" table, appends new rows to `tenders.csv` (dedup by `(site, reference_no)`). |
| `depth-info.py` | Reads `tenders.csv`, opens each tender's detail page, extracts fields (organisation, value, dates, description) and downloads attached PDFs into `pdfs/`, writes `tenders_detailed.csv`. |
| `app.py` | Flask app (port 5001): lists tenders "ending soon" / "latest", `POST /scrape` runs `main.main()`. |
| `tenders.csv` | Output of `main.py` (committed). |

## Usage

```bash
pip install requests beautifulsoup4 flask
python main.py            # collect listings -> tenders.csv
python depth-info.py      # collect details + PDFs -> tenders_detailed.csv
python app.py             # http://localhost:5001
```

## How it gets past bot protection

Short answer: it barely has to. The NIC eProcurement portals expose the data
this scraper wants as **public, unauthenticated HTML**:

- The homepage renders a `<table id="activeTenders">` with the latest active tenders.
- Each tender's detail page is a signed `DirectLink` URL (`...&sp=<token>`) that
  the listing page hands out; hitting it directly returns the full page.

So there is no CAPTCHA, login, session token, or JavaScript gate on these
paths, and the scraper does none of the things that would defeat those (no
proxy/IP rotation, no cookie jar, no headless browser, no CAPTCHA solver).

The only evasion it does is look less like a script:

1. **Spoofed `User-Agent: Mozilla/5.0`** (`main.py`, `depth-info.py`) instead of
   the default `python-requests/x.y` — dodges the crudest "block non-browser UA" filter.
2. **Spoofed `Referer` + `Accept-Language`** (`depth-info.py`) so detail-page
   requests look like in-site navigation.
3. **URL rewriting** (`depth-info.py` `fix_url()`): swaps `page=Home` →
   `page=FrontEndTenderDetails` on the signed link to land straight on the
   details view without walking the site's navigation flow.
4. **`time.sleep(2)`** between detail requests — polite rate limiting so a burst
   doesn't trip abuse detection.

If NIC ever puts these tables behind the search form (which does use a CAPTCHA
and a JSF `ViewState`/session), this approach stops working and would need a
browser-automation rewrite.
