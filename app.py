from flask import Flask, render_template_string
import csv
import os
from datetime import datetime

app = Flask(__name__)

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
    except:
        return datetime.max

@app.route('/')
def index():
    tenders = load_tenders()

    # Ending soon: sort by closing_date ascending
    ending_soon = sorted(tenders, key=lambda x: parse_date(x['closing_date']))

    # Latest: sort by opening_date descending
    latest = sorted(tenders, key=lambda x: parse_date(x['opening_date']), reverse=True)

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Indian Tenders</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f9f9f9; color: #333; margin: 0; padding: 0; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { text-align: center; color: #444; }
            .section { margin-bottom: 40px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h2 { color: #555; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; font-weight: bold; }
            tr:hover { background: #f1f1f1; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .no-data { text-align: center; color: #777; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Indian Tenders Dashboard</h1>
            <div class="section">
                <h2>Ending Soon</h2>
                {% if ending_soon %}
                <table>
                    <tr><th>Site</th><th>Title</th><th>Ref No</th><th>Closing Date</th><th>Opening Date</th><th>URL</th></tr>
                    {% for t in ending_soon %}
                    <tr>
                        <td>{{ t.site }}</td>
                        <td>{{ t.title }}</td>
                        <td>{{ t.reference_no }}</td>
                        <td>{{ t.closing_date }}</td>
                        <td>{{ t.opening_date }}</td>
                        <td><a href="{{ t.url }}" target="_blank">View</a></td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <p class="no-data">No tenders found.</p>
                {% endif %}
            </div>
            <div class="section">
                <h2>Latest Tenders</h2>
                {% if latest %}
                <table>
                    <tr><th>Site</th><th>Title</th><th>Ref No</th><th>Closing Date</th><th>Opening Date</th><th>URL</th></tr>
                    {% for t in latest %}
                    <tr>
                        <td>{{ t.site }}</td>
                        <td>{{ t.title }}</td>
                        <td>{{ t.reference_no }}</td>
                        <td>{{ t.closing_date }}</td>
                        <td>{{ t.opening_date }}</td>
                        <td><a href="{{ t.url }}" target="_blank">View</a></td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <p class="no-data">No tenders found.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, ending_soon=ending_soon, latest=latest)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)