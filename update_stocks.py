import csv
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

NSE_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
STOCKS_FILE = Path("stocks.json")


def download_csv(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8-sig")


def load_old_database():
    if not STOCKS_FILE.exists():
        return []

    try:
        with STOCKS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("stocks", [])
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read old stocks.json")
        return []


def main():
    old_stocks = load_old_database()

    old_stock_map = {}
    preserved_bse = {}

    for stock in old_stocks:
        symbol = str(stock.get("symbol", "")).strip().upper()
        exchange = str(stock.get("exchange", "")).strip().upper()

        if not symbol:
            continue

        key = (exchange, symbol)

        if key not in old_stock_map:
            old_stock_map[key] = stock

        if exchange == "BSE":
            preserved_bse[key] = stock

    csv_data = download_csv(NSE_URL)
    reader = csv.DictReader(io.StringIO(csv_data))

    updated_stocks = {}
    isin_reused = 0

    for row in reader:
        symbol = row.get("SYMBOL", "").strip().upper()
        name = row.get("NAME OF COMPANY", "").strip()
        isin = row.get("ISIN NUMBER", "").strip()

        if not symbol or not name:
            continue

        key = ("NSE", symbol)
        old_stock = old_stock_map.get(key, {})

        if not isin:
            isin = str(old_stock.get("isin", "")).strip()
            if isin:
                isin_reused += 1

        stock = dict(old_stock)
        stock.update({
            "symbol": symbol,
            "name": name,
            "isin": isin,
            "exchange": "NSE"
        })

        updated_stocks[key] = stock

    if not updated_stocks:
        raise RuntimeError("No NSE stocks were downloaded.")

    # Preserve existing BSE records
    updated_stocks.update(preserved_bse)

    final_stocks = list(updated_stocks.values())

    database = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "exchanges": ["NSE", "BSE"],
        "stocks": final_stocks
    }

    with STOCKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(database, file, ensure_ascii=False, indent=2)

    print(f"NSE stocks updated: {len([s for s in final_stocks if s.get('exchange') == 'NSE'])}")
    print(f"BSE stocks preserved: {len(preserved_bse)}")
    print(f"Old ISIN values reused: {isin_reused}")
    print(f"Total stocks saved: {len(final_stocks)}")


if __name__ == "__main__":
    main()
