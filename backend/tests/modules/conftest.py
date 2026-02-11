from datetime import date, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.modules.market.models import DailyPrice, Stock


@pytest.fixture(scope="function")
def market_data(db: Session):
    """
    Seeds the database with sample stock market data for testing.
    Cleans up the data afterwards.
    """
    # 1. Clean up potential existing data to avoid conflicts
    db.execute(text("DELETE FROM market.daily_prices WHERE symbol IN ('AAPL', 'GOOGL', 'TSLA', 'INACT')"))
    db.execute(text("DELETE FROM market.stocks WHERE symbol IN ('AAPL', 'GOOGL', 'TSLA', 'INACT')"))
    db.commit()

    # 2. Seed Stocks
    stocks = [
        Stock(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            exchange="NASDAQ",
            is_active=True
        ),
        Stock(
            symbol="GOOGL",
            name="Alphabet Inc.",
            sector="Technology",
            industry="Internet Content & Information",
            exchange="NASDAQ",
            is_active=True
        ),
        Stock(
            symbol="TSLA",
            name="Tesla Inc.",
            sector="Consumer Cyclical",
            industry="Auto Manufacturers",
            exchange="NASDAQ",
            is_active=True
        ),
        Stock(
            symbol="INACT",
            name="Inactive Corp",
            sector="N/A",
            industry="N/A",
            exchange="N/A",
            is_active=False
        ),
    ]
    db.add_all(stocks)
    db.commit()

    # 3. Seed Prices (only for AAPL for simplicity/focus)
    # Provide 5 days of data ending yesterday using relative dates
    today = date.today()
    prices = [
        DailyPrice(symbol="AAPL", date=today - timedelta(days=5), open=150.0, high=155.0, low=149.0, close=153.0, volume=1000),
        DailyPrice(symbol="AAPL", date=today - timedelta(days=4), open=153.0, high=158.0, low=152.0, close=157.0, volume=1100),
        DailyPrice(symbol="AAPL", date=today - timedelta(days=3), open=157.0, high=159.0, low=156.0, close=158.0, volume=1200),
        DailyPrice(symbol="AAPL", date=today - timedelta(days=2), open=158.0, high=162.0, low=158.0, close=161.0, volume=1300),
        DailyPrice(symbol="AAPL", date=today - timedelta(days=1), open=161.0, high=165.0, low=160.0, close=164.0, volume=1400),
    ]
    db.add_all(prices)
    db.commit()

    yield

    # 4. Cleanup
    db.execute(text("DELETE FROM market.daily_prices WHERE symbol IN ('AAPL', 'GOOGL', 'TSLA', 'INACT')"))
    db.execute(text("DELETE FROM market.stocks WHERE symbol IN ('AAPL', 'GOOGL', 'TSLA', 'INACT')"))
    db.commit()
