import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from urllib.parse import urljoin

INPUT_CSV = "tenders.csv"
OUTPUT_CSV = "tenders_detailed.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://govtprocurement.delhi.gov.in/",
    "Accept-Language": "en-US,en;q=0.9"
}

os.makedirs("pdfs", exist_ok=True)


def fetch_page(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def fix_url(url):
    if not url:
        return None
    if "page=Home" in url:
        return url.replace("page=Home", "page=FrontEndTenderDetails")
    return url


def extract_detail(soup, label):
    td = soup.find("td", string=lambda x: x and label.lower() in x.lower())
    if td:
        next_td = td.find_next_sibling("td")
        if next_td:
            return next_td.text.strip()
    return ""


def parse_details(html, url, row):
    soup = BeautifulSoup(html, "html.parser")

    data = {}
    data["organisation"] = extract_detail(soup, "Organisation Chain")
    data["tender_id"] = extract_detail(soup, "Tender ID")
    data["tender_type"] = extract_detail(soup, "Tender Type")
    data["title"] = extract_detail(soup, "Title")
    data["description"] = extract_detail(soup, "Work Description")
    data["value"] = extract_detail(soup, "Tender Value")
    data["location"] = extract_detail(soup, "Location")
    data["published_date"] = extract_detail(soup, "Published Date")
    data["bid_opening_date"] = extract_detail(soup, "Bid Opening Date")
    data["bid_submission_end"] = extract_detail(soup, "Bid Submission End Date")

    pdf_files = []
    ref_no = row.get("reference_no", "unknown")

    for table in soup.find_all("table", {"class": "list_table"}):
        for a in table.find_all("a", href=True):
            link = a["href"]

            if "DirectLink" in link:
                full_url = urljoin(url, link)
                filename = f"{ref_no}_{len(pdf_files)+1}.pdf"
                filepath = os.path.join("pdfs", filename)

                try:
                    pdf_res = requests.get(full_url, headers=HEADERS, timeout=10)

                    if "application/pdf" in pdf_res.headers.get("Content-Type", ""):
                        with open(filepath, "wb") as f:
                            f.write(pdf_res.content)

                        pdf_files.append(filename)
                        print(f"Downloaded: {filename}")

                except Exception as e:
                    print(f"PDF error: {e}")

    data["pdf_files"] = ",".join(pdf_files)

    return data


def load_existing_refs():
    existing = set()

    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ref = row.get("reference_no")
                if ref:
                    existing.add(ref)

    return existing


def main():
    existing_refs = load_existing_refs()
    results = []

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            ref = row.get("reference_no")

            if not ref or ref in existing_refs:
                continue

            raw_url = row.get("url")
            url = fix_url(raw_url)

            if not url or not url.startswith("http"):
                print("Skipping invalid URL:", raw_url)
                continue

            print(f"Scraping: {url}")

            html = fetch_page(url)
            if not html:
                continue

            details = parse_details(html, url, row)
            combined = {**row, **details}
            results.append(combined)

            time.sleep(2)

    if results:
        file_exists = os.path.exists(OUTPUT_CSV)

        with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerows(results)

        print(f"Saved {len(results)} tenders!")

    else:
        print("No new tenders found.")


if __name__ == "__main__":
    main()
