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
    st.title("MarketSight")
    st.caption("Streamlit frontend for market data, inference, and dataset snapshots.")


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


def prediction_metrics(payload: dict) -> None:
    cols = st.columns(5)
    cols[0].metric("Current Price", f"${payload['current_price']:.2f}")
    cols[1].metric("Predicted Price", f"${payload['predicted_price']:.2f}")
    cols[2].metric("Predicted Return", f"{payload['predicted_return']:.2f}%")
    confidence = payload.get("confidence")
    cols[3].metric("Confidence", "N/A" if confidence is None else f"{confidence:.2f}")
    cols[4].metric("Model Version", payload["model_version"])
    st.caption(f"Prediction date: {payload['prediction_date']}")


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
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["volume"],
            name="Volume",
            marker_color="#9ec5fe",
            opacity=0.25,
            yaxis="y2",
        )
    )
    if prediction:
        prediction_date = pd.to_datetime(prediction["prediction_date"], utc=True)
        fig.add_trace(
            go.Scatter(
                x=[df["date"].iloc[-1], prediction_date],
                y=[df["close"].iloc[-1], prediction["predicted_price"]],
                mode="lines+markers",
                name="Prediction",
                line={"color": "#f59f00", "dash": "dash", "width": 3},
            )
        )

    fig.update_layout(
        title=title,
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Price",
        yaxis2={"title": "Volume", "overlaying": "y", "side": "right", "showgrid": False},
        legend={"orientation": "h", "y": 1.02, "x": 1, "xanchor": "right"},
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        height=520,
    )
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
        st.dataframe(df, use_container_width=True, hide_index=True)
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

    search = st.text_input("Search by symbol or company name")
    filtered = df
    if search:
        match = search.strip().lower()
        filtered = df[
            df["symbol"].str.lower().str.contains(match)
            | df["name"].str.lower().str.contains(match)
        ]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    options = filtered["symbol"].tolist() or df["symbol"].tolist()
    default_symbol = st.session_state.get("selected_symbol", options[0])
    if default_symbol not in options:
        default_symbol = options[0]

    symbol = st.selectbox("Stock detail", options, index=options.index(default_symbol))
    st.session_state["selected_symbol"] = symbol
    detail = next(stock for stock in stocks if stock["symbol"] == symbol)

    days = st.select_slider("History window", options=[30, 90, 180, 365, 730], value=365)
    with st.spinner("Loading OHLC data..."):
        chart_df = ohlc_dataframe(symbol, days)
    if chart_df.empty:
        st.warning("No OHLC data is available for this symbol.")
        return

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

    meta_cols = st.columns(4)
    meta_cols[0].metric("Latest Close", f"${chart_df['close'].iloc[-1]:.2f}")
    meta_cols[1].metric("Latest Volume", f"{int(chart_df['volume'].iloc[-1]):,}")
    meta_cols[2].metric("Sector", detail.get("sector") or "N/A")
    meta_cols[3].metric("Exchange", detail.get("exchange") or "N/A")
    st.json(detail, expanded=False)


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
    st.dataframe(df, use_container_width=True, hide_index=True)

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
