from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

router = APIRouter()

# --- Load Environment & Unified DB ---
load_dotenv('/home/cosc-admin/the-project-maverick/.env')

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "changethis")
DB_NAME = os.getenv("POSTGRES_DB", "app")
DB_HOST = os.getenv("POSTGRES_HOST", "db")  # Important: in docker, host is 'db'
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

SNAPSHOT_DIR = os.getenv("SNAPSHOT_DIR", "/data/datasets")  # Expected Host Mount Path
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

class SnapshotRequest(BaseModel):
    ticker: str = "ALL"  # "ALL" will query all 29 stocks, or provide specific like "AAPL"
    start_date: str = None
    end_date: str = None
    format: str = "parquet"  # "parquet", "csv", or "both"


def get_db_engine():
    """Builds connection to current source, isolated for easy future swaps."""
    conn_str = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(conn_str)


def get_all_tables():
    """Retrieves all data tables from the 'market' schema."""
    engine = get_db_engine()
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'market'"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        # Exclude metadata tables
        tables = [row[0] for row in result if row[0] not in ('daily_prices', 'stocks')]
    return tables


@router.post("/build-snapshot")
def build_snapshot(req: SnapshotRequest):
    """
    Extracts data from the active DB and saves a Parquet and/or CSV file
    to the unified unified snapshot directory. Can do single ticker or ALL.
    """
    try:
        t0 = time.time()
        engine = get_db_engine()
        
        tickers_to_process = get_all_tables() if req.ticker.upper() == "ALL" else [req.ticker]
        if not tickers_to_process:
            raise HTTPException(status_code=404, detail="No valid ticker tables found in database.")
            
        all_dfs = []
        for tick in tickers_to_process:
            query = f'SELECT * FROM market."{tick}"'
            conditions = []
            if req.start_date:
                conditions.append(f"date >= '{req.start_date}'")
            if req.end_date:
                conditions.append(f"date <= '{req.end_date}'")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY date ASC"
            
            with engine.connect() as conn:
                df = pd.read_sql(text(query), conn)
            
            if not df.empty:
                # Keep track of which stock this data belongs to
                if 'symbol' not in df.columns:
                    df['symbol'] = tick
                all_dfs.append(df)
                
        if not all_dfs:
            raise HTTPException(status_code=404, detail=f"No data found for requested parameters.")
            
        final_df = pd.concat(all_dfs, ignore_index=True)
        timestamp_label = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        results = {}
        
        # 2. Build snapshot files
        formats_to_build = ["parquet", "csv"] if req.format == "both" else [req.format.lower()]
        for fmt in formats_to_build:
            filename = f"snapshot_{req.ticker}_{timestamp_label}.{fmt}"
            filepath = os.path.join(SNAPSHOT_DIR, filename)
            
            if fmt == "parquet":
                table = pa.Table.from_pandas(final_df)
                pq.write_table(table, filepath)
                results['parquet_file'] = filename
            elif fmt == "csv":
                final_df.to_csv(filepath, index=False)
                results['csv_file'] = filename
                
        t1 = time.time()
        results.update({
            'status': "success",
            'tickers_processed': len(tickers_to_process),
            'total_rows_extracted': len(final_df),
            'extraction_dir': SNAPSHOT_DIR,
            'time_taken_sec': round(t1 - t0, 3)
        })
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snapshots")
def list_snapshots():
    """Lists all available generated snapshots in the unified directory."""
    if not os.path.exists(SNAPSHOT_DIR):
        return {"snapshots": [], "directory": SNAPSHOT_DIR}
        
    snapshot_info = []
    for f in os.listdir(SNAPSHOT_DIR):
        fpath = os.path.join(SNAPSHOT_DIR, f)
        if os.path.isfile(fpath):
            size_mb = os.path.getsize(fpath) / (1024 * 1024)
            snapshot_info.append({"filename": f, "size_mb": round(size_mb, 2)})
            
    return {"directory": SNAPSHOT_DIR, "snapshots": snapshot_info}


@router.get("/snapshots/download/{filename}")
def download_snapshot(filename: str):
    """Serves a specific generated snapshot file for download over HTTP."""
    filepath = os.path.join(SNAPSHOT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Snapshot file not found.")
        
    return FileResponse(path=filepath, filename=filename, media_type='application/octet-stream')
