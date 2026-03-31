"""
Populates dw.dim_instrument and dw.dim_company for all 503 symbols in ml.market_data_15m.
Uses yfinance to fetch company metadata. Upserts so existing records are preserved.
"""
import time
import psycopg2
import yfinance as yf
from datetime import datetime

DSN = "host=localhost port=5432 dbname=app user=postgres password=changethis"

conn = psycopg2.connect(DSN)
conn.autocommit = False
cur = conn.cursor()

# --- Get all symbols from ml.market_data_15m ---
cur.execute("SELECT DISTINCT symbol FROM ml.market_data_15m ORDER BY symbol;")
all_symbols = [r[0] for r in cur.fetchall()]
print(f"Total symbols in ml.market_data_15m: {len(all_symbols)}")

# --- Get already-existing symbols in dim_instrument ---
cur.execute("SELECT symbol FROM dw.dim_instrument;")
existing = {r[0] for r in cur.fetchall()}
print(f"Already in dw.dim_instrument: {len(existing)}")

new_symbols = [s for s in all_symbols if s not in existing]
print(f"New symbols to add: {len(new_symbols)}")

# --- Fetch metadata from yfinance in batches ---
def fetch_info(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
        return info
    except Exception as e:
        print(f"  WARNING: yfinance failed for {symbol}: {e}")
        return {}

print("\nFetching yfinance metadata...")
results = []
for i, sym in enumerate(all_symbols):
    info = fetch_info(sym)
    results.append((sym, info))
    if (i + 1) % 50 == 0:
        print(f"  {i+1}/{len(all_symbols)} fetched...")
    time.sleep(0.05)  # avoid rate limiting

print(f"Done fetching. Upserting into DB...")

inserted_instrument = 0
inserted_company = 0

for sym, info in results:
    name = info.get("longName") or info.get("shortName") or sym
    currency = info.get("currency", "USD")
    instrument_type = "stock"

    # --- Upsert dw.dim_instrument ---
    cur.execute("""
        INSERT INTO dw.dim_instrument (instrument_type, symbol, name, currency)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (symbol) DO UPDATE SET
            name = EXCLUDED.name,
            currency = EXCLUDED.currency
    """, (instrument_type, sym, name, currency))
    inserted_instrument += 1

    # --- Upsert dw.dim_company ---
    sector = info.get("sector") or None
    industry = info.get("industry") or None
    company_name = name
    ceo = None
    officers = info.get("companyOfficers", [])
    for o in officers:
        if "CEO" in (o.get("title") or ""):
            ceo = o.get("name")
            break

    full_time_employees = info.get("fullTimeEmployees") or None
    country = info.get("country") or None
    state = info.get("state") or None
    city = info.get("city") or None
    zip_code = info.get("zip") or None
    address = info.get("address1") or None
    ipo_date = None
    ipo_raw = info.get("firstTradeDateEpochUtc")
    if ipo_raw:
        try:
            ipo_date = datetime.utcfromtimestamp(ipo_raw).date()
        except Exception:
            pass

    is_etf = info.get("quoteType", "") == "ETF"
    is_fund = info.get("quoteType", "") in ("MUTUALFUND", "FUND")

    cur.execute("SELECT sk_company_id FROM dw.dim_company WHERE symbol = %s", (sym,))
    row = cur.fetchone()
    if row:
        cur.execute("""
            UPDATE dw.dim_company SET
                company_name = %s, ceo = %s, sector = %s, industry = %s,
                full_time_employees = %s, country = %s, state = %s, city = %s,
                zip = %s, address = %s, ipo_date = %s, is_active = true,
                row_effective_ts = NOW()
            WHERE symbol = %s
        """, (company_name, ceo, sector, industry, full_time_employees,
              country, state, city, zip_code, address, ipo_date, sym))
    else:
        cur.execute("""
            INSERT INTO dw.dim_company (
                symbol, company_name, ceo, currency, sector, industry,
                full_time_employees, country, state, city, zip, address,
                ipo_date, is_active, is_etf, is_fund, row_effective_ts
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, true, %s, %s, NOW())
        """, (sym, company_name, ceo, currency, sector, industry,
              full_time_employees, country, state, city, zip_code, address,
              ipo_date, is_etf, is_fund))
    inserted_company += 1

print("Committing...")
conn.commit()
cur.close()
conn.close()

print(f"\nDone!")
print(f"  dw.dim_instrument: {inserted_instrument} upserted")
print(f"  dw.dim_company:    {inserted_company} upserted")
