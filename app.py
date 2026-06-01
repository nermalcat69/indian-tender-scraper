from flask import Flask, render_template, redirect, url_for, flash
import csv
import os
from datetime import datetime
import main as scraper
from sites import SITES

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

CSV_FILE = "tenders.csv"

def load_tenders():
    tenders = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tenders.append(row)
    return tenders

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return datetime.max

@app.route('/')
def index():
    tenders = load_tenders()
    ending_soon = sorted(tenders, key=lambda x: parse_date(x['closing_date']))
    latest = sorted(tenders, key=lambda x: parse_date(x['opening_date']), reverse=True)
    return render_template(
        "index.html",
        ending_soon=ending_soon,
        latest=latest,
        total_sites=len(SITES),
        total_tenders=len(tenders),
    )

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        scraper.main()
        flash("Scrape complete.", "success")
    except Exception as e:
        flash(f"Scrape failed: {e}", "error")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)
