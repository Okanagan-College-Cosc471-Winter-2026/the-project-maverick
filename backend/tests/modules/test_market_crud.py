from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.modules.market import crud

def test_get_active_stocks_ordered(db: Session, market_data):
    stocks = crud.get_active_stocks(db)
    # Check if ordered by symbol
    symbols = [s.symbol for s in stocks]
    assert symbols == sorted(symbols)
    # Check if only active stocks are returned ("INACT" should act exist but check logic)
    # Actually `market_data` inserts "INACT" with is_active=False
    assert "INACT" not in symbols
    assert "AAPL" in symbols

def test_get_stock_returns_none_for_missing(db: Session):
    stock = crud.get_stock(db, "NONEXISTENT")
    assert stock is None

def test_get_stock_uppercases_symbol(db: Session, market_data):
    # Pass lowercase, expect match
    stock = crud.get_stock(db, "aapl")
    assert stock is not None
    assert stock.symbol == "AAPL"

def test_get_daily_prices_date_range(db: Session, market_data):
    # Using AAPL which has 5 days of data ending yesterday seeded in market_data
    # Let's request only the last 2 days
    today = date.today()
    start_date = today - timedelta(days=2)
    end_date = today
    
    prices = crud.get_daily_prices(db, "AAPL", start=start_date, end=end_date)
    # Should return data for today-2 and today-1 (if seeded up to today-1)
    # market_data seeds: today-5, today-4, today-3, today-2, today-1
    # So expected dates: today-2, today-1
    assert len(prices) == 2
    assert prices[0].date == today - timedelta(days=2) or prices[1].date == today - timedelta(days=2)
