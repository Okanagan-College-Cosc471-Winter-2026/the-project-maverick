from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api import ApiError, build_snapshot, download_snapshot, get_ohlc, health_check, list_snapshots, list_stocks, predict

st.set_page_config(
    page_title="MarketSight Streamlit",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

TABLE_HEIGHT = 420


@st.cache_data(ttl=300, show_spinner=False)
def load_stocks() -> list[dict]:
    return list_stocks()


@st.cache_data(ttl=300, show_spinner=False)
def load_ohlc(symbol: str, days: int) -> list[dict]:
    return get_ohlc(symbol, days)


@st.cache_data(ttl=60, show_spinner=False)
def load_snapshots() -> dict:
    return list_snapshots()


def render_header() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        .ms-panel {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(248,250,252,0.96), rgba(255,255,255,0.98));
            margin-bottom: 1rem;
        }
        .ms-kicker {
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.72rem;
            color: #64748b;
            margin-bottom: 0.35rem;
        }
        .ms-title {
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.05;
            color: #0f172a;
            margin-bottom: 0.3rem;
        }
        .ms-subtitle {
            color: #475569;
            font-size: 0.98rem;
            max-width: 56rem;
        }
        </style>
        <div class="ms-panel">
            <div class="ms-kicker">Market Dashboard</div>
            <div class="ms-title">MarketSight</div>
            <div class="ms-subtitle">
                Streamlit frontend for market data, inference, and dataset snapshots.
                The layout is optimized for fast scanning instead of raw data dumps.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stocks_dataframe(stocks: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(stocks)
    if df.empty:
        return df
    for col in ("sector", "industry", "exchange"):
        if col in df.columns:
            df[col] = df[col].fillna("N/A")
    return df.sort_values(["symbol"]).reset_index(drop=True)


def ohlc_dataframe(symbol: str, days: int) -> pd.DataFrame:
    raw = load_ohlc(symbol, days)
    df = pd.DataFrame(raw)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.sort_values("date").reset_index(drop=True)


def format_stock_table(df: pd.DataFrame, height: int = TABLE_HEIGHT) -> None:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=height,
        column_config={
            "symbol": st.column_config.TextColumn("Symbol", width="small"),
            "name": st.column_config.TextColumn("Company", width="medium"),
            "sector": st.column_config.TextColumn("Sector", width="medium"),
            "industry": st.column_config.TextColumn("Industry", width="medium"),
            "exchange": st.column_config.TextColumn("Exchange", width="small"),
        },
    )


def format_snapshot_table(df: pd.DataFrame) -> None:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=TABLE_HEIGHT,
        column_config={
            "filename": st.column_config.TextColumn("File", width="large"),
            "size_mb": st.column_config.NumberColumn("Size (MB)", format="%.2f"),
        },
    )


def prediction_metrics(payload: dict) -> None:
    cols = st.columns(5)
    cols[0].metric("Latest Price", f"${payload['current_price']:.2f}")
    cols[1].metric("Forecast Price", f"${payload['predicted_price']:.2f}")
    cols[2].metric("Predicted Return", f"{payload['predicted_return']:.2f}%")
    confidence = payload.get("confidence")
    cols[3].metric("Confidence", "N/A" if confidence is None else f"{confidence:.2f}")
    cols[4].metric("Model Version", payload["model_version"])
    st.caption(
        f"Forecast is anchored to the latest available bar in the dataset. "
        f"Model horizon reference: {payload['prediction_date']}"
    )


def build_price_chart(df: pd.DataFrame, title: str, prediction: dict | None = None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="OHLC",
            increasing_line_color="#0f766e",
            decreasing_line_color="#b91c1c",
            increasing_fillcolor="#14b8a6",
            decreasing_fillcolor="#ef4444",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["volume"],
            name="Volume",
            marker_color="#94a3b8",
            opacity=0.18,
            yaxis="y2",
        )
    )
    if prediction:
        fig.add_trace(
            go.Scatter(
                x=[df["date"].iloc[-1]],
                y=[prediction["predicted_price"]],
                mode="markers",
                name="Prediction",
                marker={"size": 10, "color": "#f59e0b", "symbol": "diamond"},
            )
        )
        fig.add_annotation(
            x=df["date"].iloc[-1],
            y=prediction["predicted_price"],
            text=f"Pred ${prediction['predicted_price']:.2f}",
            showarrow=True,
            arrowhead=2,
            ax=32,
            ay=-40,
            bgcolor="rgba(245,158,11,0.12)",
            bordercolor="#f59e0b",
            font={"size": 11, "color": "#92400e"},
        )

    latest_close = float(df["close"].iloc[-1])
    fig.update_layout(
        title=title,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="#fcfcfd",
        xaxis_title=None,
        yaxis_title="Price",
        yaxis2={"title": "Volume", "overlaying": "y", "side": "right", "showgrid": False},
        legend={"orientation": "h", "y": 1.02, "x": 1, "xanchor": "right"},
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        height=560,
        hovermode="x unified",
        dragmode="pan",
    )
    fig.update_xaxes(
        showgrid=False,
        rangeslider_visible=False,
        rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[16, 9.5], pattern="hour"),
        ],
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)")
    fig.add_hline(y=latest_close, line_width=1, line_dash="dot", line_color="#94a3b8")
    return fig


def render_overview(stocks: list[dict]) -> None:
    st.subheader("Overview")
    healthy = False
    health_error = None
    try:
        healthy = health_check()
    except Exception as exc:  # noqa: BLE001
        health_error = str(exc)

    sectors = sorted({stock["sector"] for stock in stocks if stock.get("sector")})
    cols = st.columns(3)
    cols[0].metric("Tracked Stocks", len(stocks))
    cols[1].metric("Sectors", len(sectors))
    cols[2].metric("API Status", "Online" if healthy else "Unavailable")
    if health_error:
        st.warning(f"Health check failed: {health_error}")

    df = stocks_dataframe(stocks)
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("#### Coverage")
        preview = df[["symbol", "name", "sector", "exchange"]].head(12)
        format_stock_table(preview, height=460)
    with right:
        st.markdown("#### Sector Breakdown")
        if sectors:
            sector_counts = df[df["sector"] != "N/A"]["sector"].value_counts()
            st.bar_chart(sector_counts)
        else:
            st.info("No sector metadata available.")


def render_stocks(stocks: list[dict]) -> None:
    st.subheader("Stocks")
    df = stocks_dataframe(stocks)
    if df.empty:
        st.info("No stocks are available.")
        return

    controls_left, controls_mid, controls_right = st.columns([1.7, 1, 1.1])
    search = controls_left.text_input("Search by symbol or company name")
    sectors = ["All"] + sorted([sector for sector in df["sector"].unique() if sector != "N/A"])
    sector_filter = controls_mid.selectbox("Sector", sectors)
    days = controls_right.select_slider("History window", options=[7, 30, 90, 180, 365, 730], value=7)

    filtered = df.copy()
    if search:
        match = search.strip().lower()
        filtered = filtered[
            filtered["symbol"].str.lower().str.contains(match)
            | filtered["name"].str.lower().str.contains(match)
        ]
    if sector_filter != "All":
        filtered = filtered[filtered["sector"] == sector_filter]

    if filtered.empty:
        st.warning("No stocks match the current filters.")
        return

    options = filtered["symbol"].tolist()
    default_symbol = st.session_state.get("selected_symbol", options[0])
    if default_symbol not in options:
        default_symbol = options[0]

    select_col, status_col = st.columns([1.2, 2.8], gap="large")
    with select_col:
        symbol = st.selectbox("Stock detail", options, index=options.index(default_symbol))
    st.session_state["selected_symbol"] = symbol
    detail = next(stock for stock in stocks if stock["symbol"] == symbol)

    with status_col:
        st.markdown(f"### {detail['name']}")
        st.caption(f"{symbol}  |  {detail.get('sector') or 'N/A'}  |  {detail.get('exchange') or 'N/A'}")

    with st.spinner("Loading OHLC data..."):
        chart_df = ohlc_dataframe(symbol, days)
    if chart_df.empty:
        st.warning("No OHLC data is available for this symbol.")
        return

    latest_close = float(chart_df["close"].iloc[-1])
    first_close = float(chart_df["close"].iloc[0])
    period_return = ((latest_close / first_close) - 1) * 100 if first_close else 0.0
    avg_volume = float(chart_df["volume"].tail(min(len(chart_df), 20)).mean())

    meta_cols = st.columns(4)
    meta_cols[0].metric("Latest Close", f"${latest_close:.2f}")
    meta_cols[1].metric("Period Return", f"{period_return:.2f}%")
    meta_cols[2].metric("Avg Volume (20)", f"{int(avg_volume):,}")
    meta_cols[3].metric("Bars Loaded", f"{len(chart_df):,}")

    show_prediction = st.toggle("Overlay model prediction", value=False)
    prediction = None
    if show_prediction:
        try:
            prediction = predict(symbol)
            prediction_metrics(prediction)
        except ApiError as exc:
            st.error(str(exc))

    st.plotly_chart(
        build_price_chart(chart_df, f"{detail['name']} ({symbol})", prediction),
        use_container_width=True,
    )

    info_tab, data_tab = st.tabs(["Summary", "Raw Data"])
    with info_tab:
        info_left, info_right = st.columns([1, 1])
        with info_left:
            st.markdown("#### Company Context")
            st.write(f"Sector: `{detail.get('sector') or 'N/A'}`")
            st.write(f"Industry: `{detail.get('industry') or 'N/A'}`")
            st.write(f"Exchange: `{detail.get('exchange') or 'N/A'}`")
        with info_right:
            st.markdown("#### Recent Range")
            st.write(f"High: `${float(chart_df['high'].max()):.2f}`")
            st.write(f"Low: `${float(chart_df['low'].min()):.2f}`")
            st.write(f"Latest Volume: `{int(chart_df['volume'].iloc[-1]):,}`")
    with data_tab:
        raw_view = chart_df[["date", "open", "high", "low", "close", "volume"]].copy()
        st.dataframe(
            raw_view.tail(200).sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True,
            height=420,
            column_config={
                "date": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm"),
                "open": st.column_config.NumberColumn("Open", format="$%.2f"),
                "high": st.column_config.NumberColumn("High", format="$%.2f"),
                "low": st.column_config.NumberColumn("Low", format="$%.2f"),
                "close": st.column_config.NumberColumn("Close", format="$%.2f"),
                "volume": st.column_config.NumberColumn("Volume", format="%d"),
            },
        )


def render_predictions(stocks: list[dict]) -> None:
    st.subheader("Predictions")
    symbols = [stock["symbol"] for stock in stocks]
    if not symbols:
        st.info("No stocks available for prediction.")
        return

    symbol = st.selectbox("Symbol", symbols, key="prediction_symbol")
    if st.button("Generate Prediction", type="primary"):
        with st.spinner("Running inference..."):
            try:
                payload = predict(symbol)
            except ApiError as exc:
                st.error(str(exc))
                return
        prediction_metrics(payload)
        chart_df = ohlc_dataframe(symbol, 365)
        if not chart_df.empty:
            st.plotly_chart(
                build_price_chart(chart_df, f"{symbol} Price History", payload),
                use_container_width=True,
            )
        st.caption("Prediction is displayed against the most recent 365-bar history.")


def render_snapshots() -> None:
    st.subheader("Snapshots")
    with st.form("build_snapshot"):
        ticker = st.text_input("Ticker", value="ALL", help="Use ALL for every stock.")
        left, right = st.columns(2)
        start_date = left.text_input("Start date", value="", placeholder="YYYY-MM-DD")
        end_date = right.text_input("End date", value="", placeholder="YYYY-MM-DD")
        file_format = st.selectbox("Format", ["parquet", "csv", "both"])
        submitted = st.form_submit_button("Build Snapshot", type="primary")

    if submitted:
        payload = {
            "ticker": ticker or "ALL",
            "start_date": start_date or None,
            "end_date": end_date or None,
            "format": file_format,
        }
        with st.spinner("Building snapshot..."):
            try:
                result = build_snapshot(payload)
            except ApiError as exc:
                st.error(str(exc))
            else:
                st.success(
                    f"Created snapshot for {result['tickers_processed']} ticker(s), "
                    f"{result['total_rows_extracted']} rows."
                )
                st.json(result, expanded=False)
                load_snapshots.clear()

    try:
        payload = load_snapshots()
    except ApiError as exc:
        st.error(str(exc))
        return

    snapshots = payload.get("snapshots", [])
    st.caption(f"Snapshot directory: {payload.get('directory', 'unknown')}")
    if not snapshots:
        st.info("No generated snapshots yet.")
        return

    df = pd.DataFrame(snapshots).sort_values("filename").reset_index(drop=True)
    format_snapshot_table(df)

    selected_file = st.selectbox("Download snapshot", df["filename"].tolist())
    if st.button("Prepare Download"):
        with st.spinner("Fetching snapshot..."):
            try:
                file_obj = download_snapshot(selected_file)
            except ApiError as exc:
                st.error(str(exc))
                return
        st.download_button(
            label=f"Download {selected_file}",
            data=file_obj.getvalue(),
            file_name=selected_file,
            mime="application/octet-stream",
        )


def main() -> None:
    render_header()
    try:
        stocks = load_stocks()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load market data: {exc}")
        st.stop()

    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Stocks", "Predictions", "Snapshots"],
    )
    st.sidebar.caption(f"Loaded at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    if page == "Overview":
        render_overview(stocks)
    elif page == "Stocks":
        render_stocks(stocks)
    elif page == "Predictions":
        render_predictions(stocks)
    else:
        render_snapshots()


if __name__ == "__main__":
    main()
