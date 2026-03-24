"""Market module database queries against the dw warehouse schema."""

from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

STOCK_METADATA_QUERY = text(
    """
    SELECT DISTINCT
        i.symbol AS symbol,
        COALESCE(c.company_name, i.name, i.symbol) AS name,
        c.sector AS sector,
        c.industry AS industry,
        e.exchange_code AS exchange
    FROM dw.fact_15min_stock_price f
    JOIN dw.dim_instrument i
      ON f.fk_instrument_id = i.sk_instrument_id
    LEFT JOIN dw.dim_company c
      ON f.fk_company_id = c.sk_company_id
    LEFT JOIN dw.dim_exchange e
      ON f.fk_exchange_id = e.sk_exchange_id
    """
)


@dataclass
class StockRecord:
    symbol: str
    name: str
    sector: str | None
    industry: str | None
    exchange: str | None


def get_active_stocks(session: Session) -> list[StockRecord]:
    """Return all active stocks from the warehouse dimensions, ordered by symbol."""
    rows = session.execute(
        text(
            f"""
            {STOCK_METADATA_QUERY.text}
            WHERE COALESCE(c.is_active, TRUE) IS TRUE
            ORDER BY i.symbol
            """
        )
    ).fetchall()
    return [
        StockRecord(
            symbol=row.symbol,
            name=row.name,
            sector=row.sector,
            industry=row.industry,
            exchange=row.exchange,
        )
        for row in rows
    ]


def get_stock(session: Session, symbol: str) -> StockRecord | None:
    """Return a single stock by symbol, or None."""
    row = session.execute(
        text(
            f"""
            {STOCK_METADATA_QUERY.text}
            WHERE i.symbol = :symbol
            ORDER BY i.symbol
            LIMIT 1
            """
        ),
        {"symbol": symbol.upper()},
    ).fetchone()
    if row is None:
        return None
    return StockRecord(
        symbol=row.symbol,
        name=row.name,
        sector=row.sector,
        industry=row.industry,
        exchange=row.exchange,
    )


def get_daily_prices(
    session: Session,
    symbol: str,
    start: date,
    end: date,
) -> list[Any]:
    """Return OHLC rows for a symbol within a date range."""
    return list(
        session.execute(
            text(
                """
                SELECT
                    d.datetime AS date,
                    f.open_price::numeric AS open,
                    f.high_price::numeric AS high,
                    f.low_price::numeric AS low,
                    f.close_price::numeric AS close,
                    f.volume::numeric AS volume
                FROM dw.fact_15min_stock_price f
                JOIN dw.dim_date d ON f.fk_date_id = d.sk_date_id
                JOIN dw.dim_instrument i ON f.fk_instrument_id = i.sk_instrument_id
                WHERE i.symbol = :symbol
                  AND d.date >= :start
                  AND d.date <= :end
                ORDER BY d.datetime ASC
                """
            ),
            {"symbol": symbol.upper(), "start": start, "end": end},
        ).fetchall()
    )


def get_coverage(session: Session, symbol: str) -> dict[str, Any]:
    """Return earliest date, latest date, and row count for a symbol."""
    row = session.execute(
        text(
            """
            SELECT
                MIN(d.date)::date,
                MAX(d.date)::date,
                COUNT(*)
            FROM dw.fact_15min_stock_price f
            JOIN dw.dim_date d ON f.fk_date_id = d.sk_date_id
            JOIN dw.dim_instrument i ON f.fk_instrument_id = i.sk_instrument_id
            WHERE i.symbol = :symbol
            """
        ),
        {"symbol": symbol.upper()},
    ).one()
    return {"data_from": row[0], "data_to": row[1], "rows": row[2]}


def get_bars_for_features(session: Session, symbol: str, trading_days: int = 75) -> list[Any]:
    """
    Return the most recent `trading_days` worth of 15-min bars for feature engineering,
    including trade_count and vwap.  Bars are returned oldest-first.
    """
    results = session.execute(
        text(
            """
            SELECT date, open, high, low, close, volume, trade_count, vwap FROM (
                SELECT
                    d.datetime AS date,
                    f.open_price::float AS open,
                    f.high_price::float AS high,
                    f.low_price::float AS low,
                    f.close_price::float AS close,
                    f.volume::float AS volume,
                    COALESCE(f.trade_count, 0)::float AS trade_count,
                    COALESCE(f.vwap, f.close_price)::float AS vwap
                FROM dw.fact_15min_stock_price f
                JOIN dw.dim_date d ON f.fk_date_id = d.sk_date_id
                JOIN dw.dim_instrument i ON f.fk_instrument_id = i.sk_instrument_id
                WHERE i.symbol = :symbol
                ORDER BY d.datetime DESC
                LIMIT :limit
            ) sub
            ORDER BY date ASC
            """
        ),
        {"symbol": symbol.upper(), "limit": trading_days * 55},
    ).fetchall()
    return list(results)


def get_ohlc(session: Session, symbol: str, days: int = 365) -> list[Any]:
    """
    Return recent OHLC data for a symbol, oldest first.

    Fetches the latest `days * 26` 15-min bars regardless of wall-clock date,
    so stale datasets still return data.
    """
    results = session.execute(
        text(
            """
            SELECT date, open, high, low, close, volume FROM (
                SELECT
                    d.datetime AS date,
                    f.open_price::numeric AS open,
                    f.high_price::numeric AS high,
                    f.low_price::numeric AS low,
                    f.close_price::numeric AS close,
                    f.volume::numeric AS volume
                FROM dw.fact_15min_stock_price f
                JOIN dw.dim_date d ON f.fk_date_id = d.sk_date_id
                JOIN dw.dim_instrument i ON f.fk_instrument_id = i.sk_instrument_id
                WHERE i.symbol = :symbol
                ORDER BY d.datetime DESC
                LIMIT :limit
            ) sub
            ORDER BY date ASC
            """
        ),
        {"symbol": symbol.upper(), "limit": days * 26},
    ).fetchall()
    return list(results)
