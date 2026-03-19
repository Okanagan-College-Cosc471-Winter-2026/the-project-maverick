#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Iterable

import psycopg


@dataclass(frozen=True)
class TableSpec:
    name: str
    columns: tuple[str, ...]
    ddl: str
    order_by: str
    post_sql: tuple[str, ...] = ()


TABLES: tuple[TableSpec, ...] = (
    TableSpec(
        name="dim_date",
        columns=(
            "sk_date_id",
            "datetime",
            "date",
            "hour",
            "minute",
            "second",
            "day_of_week",
            "day_name",
            "day_of_month",
            "day_of_year",
            "week_of_month",
            "week_of_year",
            "month",
            "month_name",
            "year",
            "quarter",
            "is_weekend",
            "is_holiday",
            "fiscal_year",
            "fiscal_quarter",
        ),
        ddl="""
        CREATE TABLE IF NOT EXISTS dw.dim_date (
            sk_date_id BIGINT PRIMARY KEY,
            datetime TIMESTAMP WITHOUT TIME ZONE,
            date DATE,
            hour INTEGER,
            minute INTEGER,
            second INTEGER,
            day_of_week INTEGER,
            day_name VARCHAR,
            day_of_month INTEGER,
            day_of_year INTEGER,
            week_of_month INTEGER,
            week_of_year INTEGER,
            month INTEGER,
            month_name VARCHAR,
            year INTEGER,
            quarter INTEGER,
            is_weekend BOOLEAN,
            is_holiday BOOLEAN,
            fiscal_year INTEGER,
            fiscal_quarter INTEGER
        )
        """,
        order_by="sk_date_id",
    ),
    TableSpec(
        name="dim_instrument",
        columns=("sk_instrument_id", "instrument_type", "symbol", "name", "currency"),
        ddl="""
        CREATE TABLE IF NOT EXISTS dw.dim_instrument (
            sk_instrument_id BIGINT PRIMARY KEY,
            instrument_type VARCHAR,
            symbol VARCHAR,
            name VARCHAR,
            currency VARCHAR
        )
        """,
        order_by="sk_instrument_id",
        post_sql=(
            "CREATE INDEX IF NOT EXISTS ix_dw_dim_instrument_symbol ON dw.dim_instrument (symbol)",
        ),
    ),
    TableSpec(
        name="dim_exchange",
        columns=("sk_exchange_id", "exchange_code", "exchange_name"),
        ddl="""
        CREATE TABLE IF NOT EXISTS dw.dim_exchange (
            sk_exchange_id BIGINT PRIMARY KEY,
            exchange_code VARCHAR,
            exchange_name VARCHAR
        )
        """,
        order_by="sk_exchange_id",
    ),
    TableSpec(
        name="dim_company",
        columns=(
            "sk_company_id",
            "symbol",
            "company_name",
            "ceo",
            "currency",
            "sector",
            "industry",
            "full_time_employees",
            "country",
            "state",
            "city",
            "zip",
            "address",
            "ipo_date",
            "is_active",
            "is_etf",
            "is_fund",
            "row_effective_ts",
            "row_end_ts",
        ),
        ddl="""
        CREATE TABLE IF NOT EXISTS dw.dim_company (
            sk_company_id BIGINT PRIMARY KEY,
            symbol VARCHAR,
            company_name VARCHAR,
            ceo VARCHAR,
            currency VARCHAR,
            sector VARCHAR,
            industry VARCHAR,
            full_time_employees INTEGER,
            country VARCHAR,
            state VARCHAR,
            city VARCHAR,
            zip VARCHAR,
            address VARCHAR,
            ipo_date DATE,
            is_active BOOLEAN,
            is_etf BOOLEAN,
            is_fund BOOLEAN,
            row_effective_ts TIMESTAMP WITHOUT TIME ZONE,
            row_end_ts TIMESTAMP WITHOUT TIME ZONE
        )
        """,
        order_by="sk_company_id",
        post_sql=(
            "CREATE INDEX IF NOT EXISTS ix_dw_dim_company_symbol ON dw.dim_company (symbol)",
        ),
    ),
    TableSpec(
        name="fact_15min_stock_price",
        columns=(
            "sk_fact_id",
            "fk_date_id",
            "fk_instrument_id",
            "fk_exchange_id",
            "fk_audit_id",
            "fk_company_id",
            "trade_count",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
            "adj_close",
            "vwap",
            "previous_close",
            "price_change",
            "price_change_pct",
            "price_range",
        ),
        ddl="""
        CREATE TABLE IF NOT EXISTS dw.fact_15min_stock_price (
            sk_fact_id BIGINT PRIMARY KEY,
            fk_date_id BIGINT,
            fk_instrument_id BIGINT,
            fk_exchange_id BIGINT,
            fk_audit_id BIGINT,
            fk_company_id BIGINT,
            trade_count INTEGER,
            open_price NUMERIC,
            high_price NUMERIC,
            low_price NUMERIC,
            close_price NUMERIC,
            volume BIGINT,
            adj_close NUMERIC,
            vwap NUMERIC,
            previous_close NUMERIC,
            price_change NUMERIC,
            price_change_pct NUMERIC,
            price_range NUMERIC
        )
        """,
        order_by="sk_fact_id",
        post_sql=(
            "CREATE INDEX IF NOT EXISTS ix_dw_fact_15min_stock_price_date_id ON dw.fact_15min_stock_price (fk_date_id)",
            "CREATE INDEX IF NOT EXISTS ix_dw_fact_15min_stock_price_instrument_id ON dw.fact_15min_stock_price (fk_instrument_id)",
            "CREATE INDEX IF NOT EXISTS ix_dw_fact_15min_stock_price_company_id ON dw.fact_15min_stock_price (fk_company_id)",
        ),
    ),
)


def get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync warehouse dw tables from source Postgres into local Postgres.",
    )
    parser.add_argument(
        "--source-host",
        default=get_env("SOURCE_POSTGRES_SERVER", "localhost"),
    )
    parser.add_argument(
        "--source-port",
        type=int,
        default=int(get_env("SOURCE_POSTGRES_PORT", "15432")),
    )
    parser.add_argument(
        "--source-db",
        default=get_env("SOURCE_POSTGRES_DB", "emilioig_db"),
    )
    parser.add_argument(
        "--source-user",
        default=get_env("SOURCE_POSTGRES_USER", ""),
    )
    parser.add_argument(
        "--source-password",
        default=get_env("SOURCE_POSTGRES_PASSWORD", ""),
    )
    parser.add_argument(
        "--dest-host",
        default=get_env("POSTGRES_SERVER", "localhost"),
    )
    parser.add_argument(
        "--dest-port",
        type=int,
        default=int(get_env("POSTGRES_PORT", "5432")),
    )
    parser.add_argument(
        "--dest-db",
        default=get_env("POSTGRES_DB", "app"),
    )
    parser.add_argument(
        "--dest-user",
        default=get_env("POSTGRES_USER", "postgres"),
    )
    parser.add_argument(
        "--dest-password",
        default=get_env("POSTGRES_PASSWORD", ""),
    )
    parser.add_argument(
        "--tables",
        default="ALL",
        help="Comma-separated subset of tables or ALL.",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate destination tables before loading.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=20000,
        help="Rows fetched per source batch.",
    )
    return parser.parse_args()


def connect(host: str, port: int, db: str, user: str, password: str) -> psycopg.Connection:
    return psycopg.connect(
        host=host,
        port=port,
        dbname=db,
        user=user,
        password=password,
    )


def selected_tables(raw_value: str) -> list[TableSpec]:
    if raw_value.upper() == "ALL":
        return list(TABLES)
    requested = {value.strip() for value in raw_value.split(",") if value.strip()}
    table_map = {table.name: table for table in TABLES}
    unknown = requested - set(table_map)
    if unknown:
        raise ValueError(f"Unknown tables requested: {', '.join(sorted(unknown))}")
    return [table_map[name] for name in TABLES if name in requested]


def ensure_destination_schema(dest_conn: psycopg.Connection, tables: Iterable[TableSpec]) -> None:
    with dest_conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS dw")
        for table in tables:
            cur.execute(table.ddl)
            for stmt in table.post_sql:
                cur.execute(stmt)
    dest_conn.commit()


def truncate_tables(dest_conn: psycopg.Connection, tables: Iterable[TableSpec]) -> None:
    ordered = [table.name for table in tables]
    with dest_conn.cursor() as cur:
        for name in reversed(ordered):
            cur.execute(f"TRUNCATE TABLE dw.{name}")
    dest_conn.commit()


def copy_table(
    source_conn: psycopg.Connection,
    dest_conn: psycopg.Connection,
    table: TableSpec,
    chunk_size: int,
) -> None:
    column_list = ", ".join(table.columns)
    select_sql = f"SELECT {column_list} FROM dw.{table.name} ORDER BY {table.order_by}"
    copy_sql = f"COPY dw.{table.name} ({column_list}) FROM STDIN"

    transferred = 0
    with source_conn.cursor(name=f"src_{table.name}") as src_cur:
        src_cur.itersize = chunk_size
        src_cur.execute(select_sql)
        with dest_conn.cursor() as dest_cur:
            with dest_cur.copy(copy_sql) as copy:
                while True:
                    rows = src_cur.fetchmany(chunk_size)
                    if not rows:
                        break
                    for row in rows:
                        copy.write_row(row)
                    transferred += len(rows)
                    print(f"[sync] {table.name}: {transferred:,} rows", flush=True)
    dest_conn.commit()


def analyze_tables(dest_conn: psycopg.Connection, tables: Iterable[TableSpec]) -> None:
    with dest_conn.cursor() as cur:
        for table in tables:
            cur.execute(f"ANALYZE dw.{table.name}")
    dest_conn.commit()


def main() -> None:
    args = parse_args()
    tables = selected_tables(args.tables)

    if not args.source_user:
        raise ValueError("Missing source user. Set SOURCE_POSTGRES_USER or pass --source-user.")

    print(
        "[connect] source="
        f"{args.source_user}@{args.source_host}:{args.source_port}/{args.source_db}"
    )
    print(
        "[connect] dest="
        f"{args.dest_user}@{args.dest_host}:{args.dest_port}/{args.dest_db}"
    )

    with connect(
        args.source_host,
        args.source_port,
        args.source_db,
        args.source_user,
        args.source_password,
    ) as source_conn, connect(
        args.dest_host,
        args.dest_port,
        args.dest_db,
        args.dest_user,
        args.dest_password,
    ) as dest_conn:
        ensure_destination_schema(dest_conn, tables)
        if args.truncate:
            print("[reset] truncating destination dw tables")
            truncate_tables(dest_conn, tables)

        for table in tables:
            print(f"[sync] starting {table.name}", flush=True)
            copy_table(source_conn, dest_conn, table, args.chunk_size)

        analyze_tables(dest_conn, tables)
        print("[done] sync complete")


if __name__ == "__main__":
    main()
