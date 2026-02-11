from sqlalchemy.orm import Session

from app.modules.market.schemas import OHLCRead, StockRead
from app.modules.market.service import MarketService


def test_list_stocks_returns_stock_read_objects(db: Session, market_data):  # noqa: ARG001
    stocks = MarketService.list_stocks(db)
    assert isinstance(stocks, list)
    assert len(stocks) > 0
    assert isinstance(stocks[0], StockRead)

    # Verify mapping
    aapl = next(s for s in stocks if s.symbol == "AAPL")
    assert aapl.name == "Apple Inc."


def test_get_ohlc_converts_timestamps(db: Session, market_data):  # noqa: ARG001
    # Test that service layer converts date objects to Unix timestamps (int)
    ohlc_data = MarketService.get_ohlc(db, "AAPL", days=10)
    assert len(ohlc_data) > 0
    item = ohlc_data[0]
    assert isinstance(item, OHLCRead)

    # Check type of 'time' field - should be int/float (Unix timestamp) not date object
    # Pydantic schema OHLCRead defines time as int
    assert isinstance(item.time, int)
    # Basic sanity check for timestamp (e.g. > year 2000)
    assert item.time > 946684800


def test_get_ohlc_empty_range(db: Session, market_data):  # noqa: ARG001
    # Request data for a range with no prices (e.g., 2 years ago)
    # Since we use days=... logic, let's pass days=1 but ensure database has no data for yesterday
    # Wait, market_data seeds data up to yesterday.
    # To test empty, let's ask for a symbol with no data
    ohlc_data = MarketService.get_ohlc(
        db, "GOOGL", days=30
    )  # GOOGL exists but has no prices in seed
    assert isinstance(ohlc_data, list)
    assert len(ohlc_data) == 0
