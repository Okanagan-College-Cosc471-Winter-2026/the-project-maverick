from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api import (
    ApiError,
    build_snapshot,
    download_snapshot,
    get_ohlc,
    health_check,
    list_snapshots,
    list_stocks,
    predict,
    sim_base,
    sim_history,
    sim_ohlc,
    sim_session,
    sim_step,
)

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


@st.cache_data(ttl=3600, show_spinner=False)
def load_sim_session() -> dict:
    return sim_session()


@st.cache_data(ttl=3600, show_spinner=False)
def load_sim_base(symbol: str) -> dict:
    return sim_base(symbol)


@st.cache_data(ttl=3600, show_spinner=False)
def load_sim_step(symbol: str, step: int) -> dict:
    return sim_step(symbol, step)


@st.cache_data(ttl=3600, show_spinner=False)
def load_sim_history(symbol: str) -> list[dict]:
    return sim_history(symbol)


@st.cache_data(ttl=3600, show_spinner=False)
def load_sim_ohlc(symbol: str) -> list[dict]:
    return sim_ohlc(symbol)


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
    path = payload.get("path", [])
    end_price = path[-1]["pred_close"] if path else payload["current_price"]
    full_return = payload.get("predicted_full_day_return", 0.0)
    direction = payload.get("predicted_direction", "—")

    cols = st.columns(4)
    cols[0].metric("Latest Price", f"${payload['current_price']:.2f}")
    cols[1].metric("Predicted EOD Price", f"${end_price:.2f}")
    cols[2].metric(
        "Predicted Full-Day Return",
        f"{full_return:.2f}%",
        delta=f"{'▲' if direction == 'up' else '▼'} {direction}",
    )
    cols[3].metric("Model Version", payload["model_version"])
    st.caption(
        f"26-bar 15-min path prediction for {payload['prediction_date'][:10]}. "
        f"Anchored to latest available bar."
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
        path = prediction.get("path", [])
        if path:
            pred_date = prediction.get("prediction_date", "")[:10]
            path_x = [f"{pred_date} {bar['bar_time']}:00" for bar in path]
            path_y = [bar["pred_close"] for bar in path]
            fig.add_trace(
                go.Scatter(
                    x=path_x,
                    y=path_y,
                    mode="lines+markers",
                    name="Predicted Path",
                    line={"color": "#f59e0b", "width": 2, "dash": "dot"},
                    marker={"size": 4, "color": "#f59e0b"},
                )
            )
            end_price = path_y[-1]
            fig.add_annotation(
                x=path_x[-1],
                y=end_price,
                text=f"Pred EOD ${end_price:.2f}",
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


# ---------------------------------------------------------------------------
# Simulation page helpers
# ---------------------------------------------------------------------------

def render_simulation(stocks: list[dict]) -> None:
    st.subheader("Simulation — 2026-03-23 Replay")

    # --- Session metadata ---
    try:
        session_info = load_sim_session()
        step_labels: list[str] = session_info.get("step_labels", [])
        step_count: int = session_info.get("steps_completed", 26)
        base_trees: int = session_info.get("base_trees", 1157)
        warm_per_step: int = session_info.get("warm_trees_per_step", 30)
    except ApiError as exc:
        st.error(f"Could not load session info: {exc}")
        return

    # --- Symbol selector ---
    symbols = [s["symbol"] for s in stocks]
    symbol = st.selectbox(
        "Select Asset",
        symbols,
        index=symbols.index("AAPL") if "AAPL" in symbols else 0,
        key="sim_symbol",
    )

    # --- Load 5-day history (Mar 17–23) from DB ---
    try:
        hist_raw = load_sim_history(symbol)
        hist_df = pd.DataFrame(hist_raw)
        hist_df["date"] = pd.to_datetime(hist_df["time"], unit="s", utc=True)
        hist_df = hist_df.sort_values("date").reset_index(drop=True)
    except ApiError as exc:
        st.error(f"Could not load history: {exc}")
        return

    # Anchor = last close of Mar 20 (end of base model training window)
    mar20 = hist_df[hist_df["trade_date"] == "2026-03-20"]
    anchor_close: float = float(mar20["close"].iloc[-1]) if not mar20.empty else None

    # Mar 23 actual close for metrics
    mar23 = hist_df[hist_df["trade_date"] == "2026-03-23"]
    if not mar23.empty:
        actual_open = float(mar23["close"].iloc[0])
        actual_close = float(mar23["close"].iloc[-1])
        actual_ret = (actual_close / actual_open - 1) * 100

    # --- Load base model prediction ---
    try:
        with st.spinner("Loading base predictions..."):
            pred_base = load_sim_base(symbol)
    except ApiError as exc:
        st.error(f"Base prediction failed: {exc}")
        return

    full_ret_base = pred_base.get("predicted_full_day_return", 0.0)
    dir_base = pred_base.get("predicted_direction", "—")

    # --- Mode toggle ---
    mode = st.radio(
        "Prediction view",
        ["Base Model (Mar 20 → Mar 23)", "Warm-Refresh Simulation"],
        horizontal=True,
        key="sim_mode",
    )

    pred_active = pred_base
    step_label: str | None = None
    total_trees = base_trees
    current_step: int = -1  # -1 = base mode

    if mode == "Warm-Refresh Simulation":
        # Read slider value first (before loading data) so we know what to fetch
        current_step = st.session_state.get("sim_step_slider", 0)
        step_label = step_labels[current_step] if current_step < len(step_labels) else str(current_step)
        total_trees = base_trees + (current_step + 1) * warm_per_step
        try:
            with st.spinner(f"Step {step_label}..."):
                pred_active = load_sim_step(symbol, current_step)
        except ApiError as exc:
            st.error(f"Step prediction failed: {exc}")
            return

    # --- Metrics row ---
    full_ret = pred_active.get("predicted_full_day_return", 0.0)
    direction = pred_active.get("predicted_direction", "—")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Base Model Trained", "2026-03-20")
    c2.metric("Prediction Target", "2026-03-23")
    c3.metric("Predicted Return", f"{full_ret:+.4f}%")
    c4.metric("Direction", direction.upper())
    if not mar23.empty:
        st.caption(f"Actual Mar 23 return: **{actual_ret:+.2f}%** | Predicted: **{full_ret:+.4f}%**")

    # ----------------------------------------------------------------
    # The chart: 5-day close line (Mar 17-23) + prediction path on Mar 23
    # Slider sits right above the chart so it doesn't cause page scroll
    # ----------------------------------------------------------------
    if mode == "Warm-Refresh Simulation":
        current_step = st.slider(
            "Intraday bar — drag to step through warm-refresh updates",
            min_value=0,
            max_value=step_count - 1,
            value=current_step,
            format="%d",
            key="sim_step_slider",
        )
        # Reload if slider moved
        if current_step != st.session_state.get("_last_step"):
            st.session_state["_last_step"] = current_step
            step_label = step_labels[current_step] if current_step < len(step_labels) else str(current_step)
            total_trees = base_trees + (current_step + 1) * warm_per_step
            try:
                pred_active = load_sim_step(symbol, current_step)
            except ApiError as exc:
                st.error(f"Step prediction failed: {exc}")
                return

    fig = go.Figure()

    # Split history into pre-Mar23 and Mar23 actual
    pre23 = hist_df[hist_df["trade_date"] < "2026-03-23"]
    on23 = hist_df[hist_df["trade_date"] == "2026-03-23"]

    # Historical line (Mar 17-20)
    fig.add_trace(go.Scatter(
        x=pre23["date"], y=pre23["close"],
        mode="lines",
        name="Historical Close (DB)",
        line={"color": "#64748b", "width": 2},
    ))

    # Mar 23 actual line
    if not on23.empty:
        # Connect last Mar-20 bar to first Mar-23 bar
        connect_x = [pre23["date"].iloc[-1], on23["date"].iloc[0]]
        connect_y = [pre23["close"].iloc[-1], on23["close"].iloc[0]]
        fig.add_trace(go.Scatter(
            x=connect_x, y=connect_y,
            mode="lines", showlegend=False,
            line={"color": "#0ea5e9", "width": 2},
        ))

        if current_step >= 0:
            # Warm-refresh: show observed bars 0→step as a distinct "Observed" trace
            observed = on23.iloc[: current_step + 1]
            fig.add_trace(go.Scatter(
                x=observed["date"], y=observed["close"],
                mode="lines",
                name=f"Mar 23 Observed (0→{step_label})",
                line={"color": "#0ea5e9", "width": 2},
            ))
            # Show remaining actual bars as a clearly visible but distinct "future reality" line
            remaining_actual = on23.iloc[current_step:]
            if len(remaining_actual) > 1:
                fig.add_trace(go.Scatter(
                    x=remaining_actual["date"], y=remaining_actual["close"],
                    mode="lines",
                    name="Mar 23 Actual — not yet seen by model",
                    line={"color": "#38bdf8", "width": 2, "dash": "dashdot"},
                    opacity=0.6,
                ))
        else:
            fig.add_trace(go.Scatter(
                x=on23["date"], y=on23["close"],
                mode="lines",
                name="Mar 23 Actual (DB)",
                line={"color": "#0ea5e9", "width": 2},
            ))

    import math

    bars = pred_active.get("bars", [])
    if bars and not on23.empty:
        if current_step >= 0:
            # Warm-refresh: anchor prediction to actual close at current step
            # Only show forward bars (step+1 → 25) so the line starts where reality is
            actual_close_at_step = float(on23["close"].iloc[current_step])
            base_log_ret = bars[current_step]["pred_log_return"]

            fwd_start = current_step  # include current bar as the anchor point
            fwd_bars = bars[fwd_start:]
            fwd_xs = [on23["date"].iloc[fwd_start + i] for i in range(len(fwd_bars)) if fwd_start + i < len(on23)]
            fwd_ys = [
                round(actual_close_at_step * math.exp(b["pred_log_return"] - base_log_ret), 4)
                for b in fwd_bars[: len(fwd_xs)]
            ]
            fig.add_trace(go.Scatter(
                x=fwd_xs, y=fwd_ys,
                mode="lines+markers",
                name=f"Warm-Refresh Prediction @ {step_label} ({total_trees:,} trees)",
                line={"color": "#f59e0b", "width": 2.5, "dash": "dot"},
                marker={"size": 4, "color": "#f59e0b"},
            ))
        elif anchor_close:
            # Base mode: full 26-bar prediction anchored to Mar 20 close
            pred_xs = [on23["date"].iloc[i] for i in range(len(bars)) if i < len(on23)]
            pred_ys = [round(anchor_close * math.exp(b["pred_log_return"]), 4) for b in bars[: len(pred_xs)]]
            fig.add_trace(go.Scatter(
                x=pred_xs, y=pred_ys,
                mode="lines+markers",
                name=f"Base Model Prediction ({base_trees:,} trees)",
                line={"color": "#f59e0b", "width": 2.5, "dash": "dot"},
                marker={"size": 4, "color": "#f59e0b"},
            ))

    # Vertical line marking start of Mar 23
    if not on23.empty:
        vline_x = on23["date"].iloc[0].strftime("%Y-%m-%d %H:%M:%S")
        fig.add_shape(
            type="line",
            x0=vline_x, x1=vline_x,
            y0=0, y1=1,
            xref="x", yref="paper",
            line={"dash": "dash", "color": "#94a3b8", "width": 1},
        )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="#fcfcfd",
        yaxis_title="Price (USD)",
        xaxis_title=None,
        height=520,
        hovermode="x unified",
        dragmode="pan",
        legend={"orientation": "h", "y": 1.04, "x": 1, "xanchor": "right"},
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        xaxis=dict(
            showgrid=False,
            rangeslider_visible=False,
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
                dict(bounds=[20, 13.5], pattern="hour"),  # UTC: 20:00=16:00ET close, 13:30=09:30ET open
            ],
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    render_header()
    try:
        stocks = load_stocks()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load market data: {exc}")
        st.stop()

    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Stocks", "Predictions", "Simulation", "Snapshots"],
    )
    st.sidebar.caption(f"Loaded at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC")

    if page == "Overview":
        render_overview(stocks)
    elif page == "Stocks":
        render_stocks(stocks)
    elif page == "Predictions":
        render_predictions(stocks)
    elif page == "Simulation":
        render_simulation(stocks)
    else:
        render_snapshots()


if __name__ == "__main__":
    main()
