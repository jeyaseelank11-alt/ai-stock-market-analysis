import csv
import io
import json
import urllib.request
from datetime import datetime, timezone

NSE_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

def download_csv(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8-sig")

def main():
    csv_data = download_csv(NSE_URL)
    reader = csv.DictReader(io.StringIO(csv_data))

    stocks = []

    for row in reader:
        symbol = row.get("SYMBOL", "").strip()
        name = row.get("NAME OF COMPANY", "").strip()
        isin = row.get("ISIN NUMBER", "").strip()

        if symbol and name:
            stocks.append({
                "symbol": symbol,
                "name": name,
                "isin": isin,
                "exchange": "NSE"
            })

    if not stocks:
        raise RuntimeError("No NSE stocks were downloaded.")

    database = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "exchanges": ["NSE", "BSE"],
        "stocks": stocks
    }

    with open("stocks.json", "w", encoding="utf-8") as file:
        json.dump(database, file, ensure_ascii=False, indent=2)

    print(f"Downloaded {len(stocks)} NSE stocks.")

if _name_ == "_main_":
    main()
