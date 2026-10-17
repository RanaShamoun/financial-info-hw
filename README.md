# Multi-Provider Stock Data Tool

A command-line Python application that looks up a stock quote using Yahoo Finance and falls back to Google Finance if the primary lookup fails. It displays the company name, latest available price, and daily price change.

This project was created as a course assignment for experimenting with financial data retrieval from multiple providers.

## Features

- Retrieves quote data from Yahoo Finance using `yfinance`.
- Falls back to Google Finance by parsing its quote page with Beautiful Soup.
- Displays the company name, price, and daily change when available.
- Continues accepting symbols until you choose to quit.
- Reports provider errors and handles unavailable network connections.

## Requirements

- Python 3
- An internet connection

## Setup

From the project directory, create and activate a virtual environment:

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

From the project directory:

```bash
python src/multi_provider_stock.py
```

Enter a ticker symbol when prompted, for example `AAPL` or `MSFT`. Enter `exit` or `quit` to close the program. Pressing Ctrl+C also exits.

## Data sources and limitations

Yahoo Finance is the primary source. If that lookup fails, the application attempts to scrape Google Finance, which may not work if the page structure changes or the request is blocked. Both services are accessed through unofficial interfaces and may limit, change, or discontinue access without notice. Quotes may be delayed or unavailable; this tool is for educational use and is not investment advice.
