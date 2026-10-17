import sys
import time
import requests
from bs4 import BeautifulSoup
import yfinance as yf

# Headers to prevent Google from blocking raw automated user-agents
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}


def fetch_from_yahoo(symbol: str) -> dict:
    """Retrieves stock data using Yahoo Finance (yfinance)."""
    ticker = yf.Ticker(symbol)
    info = ticker.info

    price = info.get("currentPrice") or info.get("regularMarketPrice")
    previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")

    if price is None or previous_close is None:
        raise ValueError("Invalid symbol or missing price data on Yahoo Finance.")

    company_name = info.get("longName") or info.get("shortName") or symbol.upper()
    change = price - previous_close
    pct_change = (change / previous_close) * 100 if previous_close != 0 else 0.0

    return {
        "source": "Yahoo Finance",
        "company_name": company_name,
        "price": price,
        "change": change,
        "pct_change": pct_change,
    }


def fetch_from_google(symbol: str, exchange: str = "NASDAQ") -> dict:
    """Retrieves stock data by scraping Google Finance (Free Web Scrape)."""
    url = f"https://www.google.com/finance/quote/{symbol}:{exchange}"
    response = requests.get(url, headers=HEADERS, timeout=5)

    if response.status_code != 200:
        raise ValueError(f"Google Finance returned HTTP status {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract price element
    price_div = soup.find("div", {"class": "YMlA3d"}) or soup.find("div", {"class": "fx4vi"})
    if not price_div:
        # Fallback query without exchange specified
        url = f"https://www.google.com/finance/quote/{symbol}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        price_div = soup.find("div", {"class": "YMlA3d"}) or soup.find("div", {"class": "fx4vi"})

    if not price_div:
        raise ValueError("Could not parse price from Google Finance HTML.")

    raw_price = price_div.text.replace("$", "").replace(",", "").strip()
    price = float(raw_price)

    # Extract company name
    name_div = soup.find("div", {"class": "zz22W"})
    company_name = name_div.text.strip() if name_div else symbol.upper()

    # Extract change and percent change
    change_div = soup.find("div", {"class": "jw8mdb"}) or soup.find("div", {"class": "Jw151b"})
    change_text = change_div.text.strip() if change_div else "+0.00 (+0.00%)"

    # Quick parsing of change string format e.g., "+0.60 (+0.55%)"
    return {
        "source": "Google Finance",
        "company_name": company_name,
        "price": price,
        "raw_change_str": change_text,
    }


def get_stock_data(symbol: str) -> None:
    """Primary routing function with built-in resilience and provider failover."""
    data = None
    
    # Provider 1: Try Yahoo Finance
    try:
        data = fetch_from_yahoo(symbol)
    except Exception as y_err:
        print(f"[Notice] Yahoo Finance lookup failed ({y_err}). Trying Google Finance fallback...")

        # Provider 2: Fallback to Google Finance
        try:
            data = fetch_from_google(symbol)
        except Exception as g_err:
            print(f"Error: Unable to retrieve data for '{symbol}' from both providers.")
            print(f"Details: Google Finance error: {g_err}\n")
            return

    # Formatting and output
    current_time = time.strftime("%a %b %d %H:%M:%S %Z %Y")
    
    print(current_time)
    print(f"{data['company_name']} ({symbol.upper()})]")

    if "change" in data:
        change_str = f"+{data['change']:.2f}" if data['change'] >= 0 else f"{data['change']:.2f}"
        pct_str = f"+{data['pct_change']:.2f}%" if data['pct_change'] >= 0 else f"{data['pct_change']:.2f}%"
        print(f"{data['price']:.2f} {change_str} ({pct_str})\n")
    else:
        # Render scraped string directly for Google fallback
        print(f"{data['price']:.2f} {data.get('raw_change_str', '')}\n")


def main():
    print("=== Multi-Source Stock Data Tool ===")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            symbol = input("Please enter a symbol:\n").strip()
            if not symbol:
                continue
            if symbol.lower() in ("exit", "quit"):
                break

            get_stock_data(symbol)

        except requests.exceptions.ConnectionError:
            print("Error: No network connection available. Please check your internet.\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting program.")
            sys.exit(0)


if __name__ == "__main__":
    main()