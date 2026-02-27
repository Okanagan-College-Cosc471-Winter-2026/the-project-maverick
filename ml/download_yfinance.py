import argparse
import datetime
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")

import pandas as pd
import requests
import yfinance as yf


def fetch_sp500_tickers() -> list[str]:
    from io import StringIO
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    html = requests.get(url, headers=headers, timeout=15).text
    tickers = pd.read_html(StringIO(html))[0]["Symbol"].tolist()
    return [t.replace(".", "-") for t in tickers]


def download_chunk(tickers: list[str], start: str, end: str) -> pd.DataFrame | None:
    try:
        data = yf.download(
            tickers,
            start=start,
            end=end,
            auto_adjust=True,   # split- and dividend-adjusted prices
            threads=True,
            progress=False,
        )
        if data.empty:
            return None

        stacked = data.stack(level=1, future_stack=True).reset_index()
        stacked = stacked.rename(columns={
            "Ticker": "symbol",
            "Date":   "date",
            "Open":   "open",
            "High":   "high",
            "Low":    "low",
            "Close":  "close",
            "Volume": "volume",
        })
        cols = [c for c in ["symbol", "date", "open", "high", "low", "close", "volume"] if c in stacked.columns]
        return stacked[cols].dropna()
    except Exception as exc:
        print(f"  [warn] chunk failed: {exc}", file=sys.stderr)
        return None


def download_data(n_tickers: int, years: int, chunk_size: int, output_file: str) -> None:
    print("Fetching S&P 500 ticker list from Wikipedia...")
    all_tickers = fetch_sp500_tickers()
    tickers = all_tickers[:n_tickers]
    print(f"  {len(tickers)} tickers selected")

    end_date   = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=years * 365)
    start_str, end_str = start_date.isoformat(), end_date.isoformat()
    print(f"  Period: {start_str} → {end_str}")

    chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
    print(f"\nDownloading in {len(chunks)} chunk(s) of up to {chunk_size} tickers...")

    frames: list[pd.DataFrame] = []
    failed_tickers: list[str] = []

    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i}/{len(chunks)}: {chunk[0]} … {chunk[-1]}")
        df = download_chunk(chunk, start_str, end_str)
        if df is not None and not df.empty:
            frames.append(df)
        else:
            failed_tickers.extend(chunk)

    if not frames:
        print("No data downloaded. Exiting.", file=sys.stderr)
        sys.exit(1)

    final_df = pd.concat(frames, ignore_index=True)
    final_df["date"] = pd.to_datetime(final_df["date"])
    final_df = final_df.sort_values(["symbol", "date"]).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    try:
        final_df.to_parquet(output_file, index=False)
    except ImportError:
        output_file = os.path.splitext(output_file)[0] + ".csv"
        print(f"[warn] pyarrow not found — saving as CSV instead: {output_file}")
        final_df.to_csv(output_file, index=False)

    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"\nSaved {len(final_df):,} rows → {output_file} ({size_mb:.1f} MB)")
    print(f"Symbols: {final_df['symbol'].nunique()} | Date range: {final_df['date'].min().date()} – {final_df['date'].max().date()}")

    if failed_tickers:
        print(f"\n[warn] {len(failed_tickers)} tickers produced no data: {failed_tickers}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download S&P 500 historical data via yfinance")
    parser.add_argument("--tickers",    type=int, default=100,   help="Number of S&P 500 tickers to download (default: 100)")
    parser.add_argument("--years",      type=int, default=10,    help="Years of history (default: 10)")
    parser.add_argument("--chunk-size", type=int, default=25,    help="Tickers per download batch (default: 25)")
    parser.add_argument("--output",     type=str, default="yfinance_sp500.parquet", help="Output parquet file path")
    args, _ = parser.parse_known_args()

    download_data(args.tickers, args.years, args.chunk_size, args.output)
