import requests
from bs4 import BeautifulSoup
import csv
import os
import re
from sites import SITES

CSV_FILE = "tenders.csv"


def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    return res.text


def parse_tenders(html, site_name, base_url):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"id": "activeTenders"})
    if not table:
        print(f"No tenders table found for {site_name}")
        return []

    tenders = []

    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        title_tag = cols[0].find("a")

        title = title_tag.text.strip() if title_tag else ""
        title = re.sub(r'^\d+\.\s*', '', title)
        link = title_tag["href"] if title_tag else ""

        ref_no = cols[1].text.strip()
        closing_date = cols[2].text.strip()
        opening_date = cols[3].text.strip()

        full_url = base_url + link if link else ""

        if title and ref_no:
            tenders.append({
                "site": site_name,
                "title": title,
                "reference_no": ref_no,
                "closing_date": closing_date,
                "opening_date": opening_date,
                "url": full_url
            })

    return tenders


def load_existing_refs():
    if not os.path.exists(CSV_FILE):
        return set()

    refs = set()
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            site = row.get("site", "Delhi Govt Procurement")
            refs.add((site, row["reference_no"]))

    return refs


def save_to_csv(tenders):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["site", "title", "reference_no", "closing_date", "opening_date", "url"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for tender in tenders:
            writer.writerow(tender)


def main():
    print("Fetching tenders from all sites...")

    existing_refs = load_existing_refs()

    all_tenders = []
    for site in SITES:
        print(f"Fetching from {site['name']}...")
        BASE_URL = site['url']
        URL = site['url'] + ('/nicgep/app' if not site['url'].endswith('/nicgep/app') else '')
        try:
            html = fetch_html(URL)
            tenders = parse_tenders(html, site['name'], BASE_URL)
            all_tenders.extend(tenders)
        except Exception as e:
            print(f"Error fetching from {site['name']}: {e}")

    new_tenders = [
        t for t in all_tenders if (t["site"], t["reference_no"]) not in existing_refs
    ]

    if not new_tenders:
        print("No new tenders found.")
        return

    save_to_csv(new_tenders)

    print(f"Saved {len(new_tenders)} new tenders.")


if __name__ == "__main__":
    main()