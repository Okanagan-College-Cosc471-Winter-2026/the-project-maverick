import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('/home/cosc-admin/the-project-maverick/ml/.env')

DB_USER = os.getenv("POSTGRES_USER", "mluser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "mlpassword")
DB_NAME = os.getenv("POSTGRES_DB", "market_data")

# Connect to localhost port 5432 which is now forwarded from the main docker db instance
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@localhost:5432/{DB_NAME}')

DATA_DIR = "/home/cosc-admin/the-project-maverick/ml/data/fmp_historical_5min"

TICKERS = ['AAPL', 'AMD', 'AMZN', 'BA', 'BABA', 'BAC', 'C', 'CSCO', 'CVX', 
           'DIS', 'F', 'GE', 'GOOGL', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 
           'MCD', 'META', 'MSFT', 'NFLX', 'NVDA', 'PFE', 'T', 'TSLA', 
           'VZ', 'WMT', 'XOM']

def clean_and_import():
    with engine.connect() as conn:
        print("Cleaning previous market schema...")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS market;"))
        # Drop tables for these tickers to ensure a clean slate
        for ticker in TICKERS:
            conn.execute(text(f'DROP TABLE IF EXISTS market."{ticker}" CASCADE;'))
        
        # Also drop daily_prices and stocks just in case to eliminate discrepancy
        conn.execute(text('DROP TABLE IF EXISTS market.daily_prices CASCADE;'))
        conn.execute(text('DROP TABLE IF EXISTS market.stocks CASCADE;'))
        conn.commit()
    
    # 2. Re-create the master stocks table with the 29 symbols
    print("Re-creating market.stocks registry...")
    stocks_df = pd.DataFrame({'symbol': TICKERS, 'name': TICKERS})
    stocks_df.to_sql('stocks', engine, schema='market', if_exists='replace', index=False)

    print("\nStarting Ingestion from FMP 5min folder...")
    count = 0
    total = len(TICKERS)
    
    for ticker in TICKERS:
        filepath = os.path.join(DATA_DIR, f"{ticker}.csv")
        if not os.path.exists(filepath):
            print(f"Skipping {ticker}, could not find {filepath}")
            continue
            
        print(f"[{count+1}/{total}] Loading {ticker}...")
        df = pd.read_csv(filepath)
        
        # Ingest efficiently
        df.to_sql(ticker, engine, schema='market', if_exists='replace', index=False, chunksize=10000, method='multi')
        print(f"  -> Ingested {len(df)} rows for {ticker}")
        
        count += 1
        
    print("\nAll complete FMP Historical data has been securely loaded into PostgreSQL!")

if __name__ == "__main__":
    clean_and_import()
