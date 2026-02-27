import requests
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()
FMP_API_KEY = os.getenv("FMP_API_KEY")

if not FMP_API_KEY:
    raise ValueError("Please set FMP_API_KEY in your .env file")

TICKERS = ['AAPL', 'AMD', 'AMZN', 'BA', 'BABA', 'BAC', 'C', 'CSCO', 'CVX', 
           'DIS', 'F', 'GE', 'GOOGL', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 
           'MCD', 'META', 'MSFT', 'NFLX', 'NVDA', 'PFE', 'T', 'TSLA', 
           'VZ', 'WMT', 'XOM']

START_DATE = "2020-07-01"
END_DATE = "2023-06-30"

OUTPUT_DIR = "/home/cosc-admin/the-project-maverick/ml/data/fmp_historical_5min"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_fmp_data(ticker, start_date, end_date):
    """Download 5-minute data from FMP API."""
    print(f"Downloading historical data for {ticker}...")
    
    # FMP has a limit on how much data can be returned in a single call for intraday
    # We might need to split this into chunks if FMP restricts the date range per API call
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/5min/{ticker}?from={start_date}&to={end_date}&apikey={FMP_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print(f"No data returned for {ticker}")
            return False
            
        df = pd.DataFrame(data)
        # Ensure column names match our existing data
        df = df.rename(columns={"date": "date", "open": "open", "low": "low", "high": "high", "close": "close", "volume": "volume"})
        
        # We only need specific columns
        df = df[['date', 'open', 'low', 'high', 'close', 'volume']]
        
        # Sort by date ascending (oldest to newest)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        output_file = os.path.join(OUTPUT_DIR, f"{ticker}.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved {len(df)} rows to {output_file}")
        
        # Be nice to the API
        time.sleep(1)
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data for {ticker}: {e}")
        return False

def main():
    success_count = 0
    for ticker in TICKERS:
        if download_fmp_data(ticker, START_DATE, END_DATE):
            success_count += 1
            
    print(f"\nDownload complete! Successfully downloaded data for {success_count}/{len(TICKERS)} tickers.")

if __name__ == "__main__":
    main()
