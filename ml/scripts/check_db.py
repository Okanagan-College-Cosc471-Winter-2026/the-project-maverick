import pandas as pd
from sqlalchemy import create_engine, text

# Database configuration (matching the notebook)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'market_data',
    'user': 'mluser',
    'password': 'mlpassword'
}

def check_db():
    connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            print("Successfully connected to the database!")
            
            # Check for tables in 'market' schema
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'market' 
            ORDER BY table_name
            LIMIT 5
            """
            tables = pd.read_sql(query, conn)
            print(f"\nFound {len(tables)} tables (showing first few):")
            print(tables)
            
            if not tables.empty:
                # Check row count for one table (e.g., first one found or 'aapl' if it exists)
                table_to_check = 'aapl' if 'aapl' in tables['table_name'].values else tables['table_name'].iloc[0]
                print(f"\nChecking row count for table: {table_to_check}")
                count_query = text(f'SELECT count(*) FROM market."{table_to_check}"')
                count = conn.execute(count_query).scalar()
                print(f"Row count: {count}")

                # Check date range
                date_query = text(f'SELECT min(date), max(date) FROM market."{table_to_check}"')
                min_date, max_date = conn.execute(date_query).fetchone()
                print(f"Date range: {min_date} to {max_date}")

    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_db()
