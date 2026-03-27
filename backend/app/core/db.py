from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    # Tables should be created with Alembic migrations
    # Base.metadata.create_all(bind=engine)
    pass
  import pandas as pd                                                                                                                                                                           
  import time                                                                                                                                                                                   
   
  t0 = time.time()                                                                                                                                                                              
  print("Loading...", flush=True)                           
  df = pd.read_parquet('/project/6065705/market_data_15m.parquet', engine='pyarrow')
  print(f"Loaded {len(df):,} rows in {time.time()-t0:.1f}s", flush=True)                                                                                                                        
                                                                                                                                                                                                
  # Fix 1: status = 'final'                                                                                                                                                                     
  df['status'] = 'final'                                                                                                                                                                        
                                                            
  # Fix 2: filter to regular session only (09:30–15:45)                                                                                                                                         
  df['window_ts'] = pd.to_datetime(df['window_ts'], utc=True)
  hour = df['window_ts'].dt.hour                                                                                                                                                                
  minute = df['window_ts'].dt.minute                        
  market = ((hour > 9) | ((hour == 9) & (minute >= 30))) & (hour < 16)                                                                                                                          
  df = df[market].copy()                                                                                                                                                                        
  print(f"After hour filter: {len(df):,} rows", flush=True)
                                                                                                                                                                                                
  # Fix 3: strip timezone (make tz-naive) — XG_boost_3.py compares tz-naive timestamps                                                                                                          
  df['window_ts'] = df['window_ts'].dt.tz_localize(None)                                                                                                                                        
                                                                                                                                                                                                
  print("Writing...", flush=True)                           
  df.to_parquet('/project/6065705/market_data_15m.parquet', index=False, compression='snappy', engine='pyarrow')
  print(f"Done in {time.time()-t0:.1f}s | rows: {len(df):,}")                                                                                                                                   
  print("Status values:", df['status'].unique())                                                                                                                                                
  print("Sample window_ts:", df['window_ts'].iloc[0], "(tz-naive:", df['window_ts'].iloc[0].tzinfo is None, ")")                                                                                
                                                    