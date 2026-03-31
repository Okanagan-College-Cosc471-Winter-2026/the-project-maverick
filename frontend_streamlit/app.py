from __future__ import annotations

import math
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
    page_title="MarketSight",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

TABLE_HEIGHT = 420

# ── Minimal CSS: tighten top padding, no other overrides ──────────────────────
st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    [data-testid="stSidebar"] .sidebar-brand {
        padding: 0.5rem 0 1rem 0;
        border-bottom: 1px solid rgba(148,163,184,0.25);
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Caches ─────────────────────────────────────────────────────────────────────

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


# ── Helpers ────────────────────────────────────────────────────────────────────

def stocks_dataframe(stocks: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(stocks)
    if df.empty:
        return df
    for col in ("sector", "industry", "exchange"):
        if col in df.columns:
            df[col] = df[col].fillna("N/A")
    return df.sort_values("symbol").reset_index(drop=True)


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
    cols[1].metric("Predicted EOD", f"${end_price:.2f}")
    cols[2].metric(
        "Full-Day Return",
        f"{full_return:.2f}%",
        delta=f"{'▲' if direction == 'up' else '▼'} {direction}",
    )
    cols[3].metric("Model", payload["model_version"])
    st.caption(
        f"26-bar 15-min path for {payload['prediction_date'][:10]}. "
        "Anchored to latest available bar."
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


# ── Pages ──────────────────────────────────────────────────────────────────────

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


def render_stocks(stocks: list[dict], sidebar_symbol: str | None = None) -> None:
    df = stocks_dataframe(stocks)
    if df.empty:
        st.info("No stocks are available.")
        return

    symbol = sidebar_symbol or (df["symbol"].iloc[0] if not df.empty else None)
    if not symbol:
        return

    detail = next((s for s in stocks if s["symbol"] == symbol), {})

    # ── Header row ─────────────────────────────────────────────────────────────
    h1, h2, h3, h4 = st.columns(4)
    with st.spinner("Loading OHLC..."):
        days = st.session_state.get("stocks_days", 30)
        chart_df = ohlc_dataframe(symbol, days)

    if chart_df.empty:
        st.warning("No OHLC data available for this symbol.")
        return

    latest_close = float(chart_df["close"].iloc[-1])
    first_close = float(chart_df["close"].iloc[0])
    period_return = ((latest_close / first_close) - 1) * 100 if first_close else 0.0
    avg_volume = float(chart_df["volume"].tail(min(len(chart_df), 20)).mean())

    h1.metric("Latest Close", f"${latest_close:.2f}")
    h2.metric("Period Return", f"{period_return:.2f}%")
    h3.metric("Avg Volume (20)", f"{int(avg_volume):,}")
    h4.metric("Bars Loaded", f"{len(chart_df):,}")

    # ── Prediction toggle (inline, above chart) ─────────────────────────────
    show_prediction = st.toggle("Overlay model prediction", value=False)
    prediction = None
    if show_prediction:
        try:
            prediction = predict(symbol)
            prediction_metrics(prediction)
        except ApiError as exc:
            st.error(str(exc))

    # ── Chart — full width ──────────────────────────────────────────────────
    st.plotly_chart(
        build_price_chart(chart_df, f"{detail.get('name', symbol)} ({symbol})", prediction),
        use_container_width=True,
    )

    # ── Info + raw data tabs below the chart ────────────────────────────────
    info_tab, data_tab = st.tabs(["Summary", "Raw Data"])
    with info_tab:
        c1, c2 = st.columns(2)
        c1.write(f"**Sector:** {detail.get('sector') or 'N/A'}")
        c1.write(f"**Industry:** {detail.get('industry') or 'N/A'}")
        c1.write(f"**Exchange:** {detail.get('exchange') or 'N/A'}")
        c2.write(f"**High:** ${float(chart_df['high'].max()):.2f}")
        c2.write(f"**Low:** ${float(chart_df['low'].min()):.2f}")
        c2.write(f"**Latest Volume:** {int(chart_df['volume'].iloc[-1]):,}")
    with data_tab:
        raw_view = chart_df[["date", "open", "high", "low", "close", "volume"]].copy()
        st.dataframe(
            raw_view.tail(200).sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True,
            height=380,
            column_config={
                "date": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm"),
                "open": st.column_config.NumberColumn("Open", format="$%.2f"),
                "high": st.column_config.NumberColumn("High", format="$%.2f"),
                "low": st.column_config.NumberColumn("Low", format="$%.2f"),
                "close": st.column_config.NumberColumn("Close", format="$%.2f"),
                "volume": st.column_config.NumberColumn("Volume", format="%d"),
            },
        )


def render_predictions(stocks: list[dict], sidebar_symbol: str | None = None) -> None:
    symbols = [s["symbol"] for s in stocks]
    if not symbols:
        st.info("No stocks available.")
        return

    symbol = sidebar_symbol or symbols[0]

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
                build_price_chart(chart_df, f"{symbol} — Predicted Path", payload),
                use_container_width=True,
            )
        st.caption("Prediction shown against the most recent 365-bar history.")


def render_simulation(stocks: list[dict], sidebar_symbol: str | None = None) -> None:
    # Session metadata (already loaded in sidebar, pass it in via session state)
    try:
        session_info = load_sim_session()
        step_labels: list[str] = session_info.get("step_labels", [])
        step_count: int = session_info.get("steps_completed", 26)
        base_trees: int = session_info.get("base_trees", 1157)
        warm_per_step: int = session_info.get("warm_trees_per_step", 30)
    except ApiError as exc:
        st.error(f"Could not load session info: {exc}")
        return

    symbols = [s["symbol"] for s in stocks]
    symbol = sidebar_symbol or ("AAPL" if "AAPL" in symbols else symbols[0])

    # ── Load history ────────────────────────────────────────────────────────
    try:
        hist_raw = load_sim_history(symbol)
        hist_df = pd.DataFrame(hist_raw)
        hist_df["date"] = pd.to_datetime(hist_df["time"], unit="s", utc=True)
        hist_df = hist_df.sort_values("date").reset_index(drop=True)
    except ApiError as exc:
        st.error(f"Could not load history: {exc}")
        return

    mar20 = hist_df[hist_df["trade_date"] == "2026-03-20"]
    anchor_close: float | None = float(mar20["close"].iloc[-1]) if not mar20.empty else None

    mar23 = hist_df[hist_df["trade_date"] == "2026-03-23"]
    actual_ret = None
    if not mar23.empty:
        actual_open = float(mar23["close"].iloc[0])
        actual_close = float(mar23["close"].iloc[-1])
        actual_ret = (actual_close / actual_open - 1) * 100

    # ── Load base prediction ────────────────────────────────────────────────
    try:
        pred_base = load_sim_base(symbol)
    except ApiError as exc:
        st.error(f"Base prediction failed: {exc}")
        return

    # ── Mode + step (read from session state set by sidebar) ────────────────
    mode = st.session_state.get("sim_mode", "Base Model (Mar 20 → Mar 23)")
    current_step = st.session_state.get("sim_step_slider", 0)

    pred_active = pred_base
    step_label: str | None = None
    total_trees = base_trees
    is_warm = mode == "Warm-Refresh Simulation"

    if is_warm:
        step_label = step_labels[current_step] if current_step < len(step_labels) else str(current_step)
        total_trees = base_trees + (current_step + 1) * warm_per_step
        try:
            pred_active = load_sim_step(symbol, current_step)
        except ApiError as exc:
            st.error(f"Step prediction failed: {exc}")
            return

    # ── Metrics row ─────────────────────────────────────────────────────────
    full_ret = pred_active.get("predicted_full_day_return", 0.0)
    direction = pred_active.get("predicted_direction", "—")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Base Trained", "2026-03-20")
    c2.metric("Target Date", "2026-03-23")
    c3.metric("Predicted Return", f"{full_ret:+.4f}%")
    c4.metric("Direction", direction.upper())

    if actual_ret is not None:
        mode_label = f"step {current_step} ({step_label})" if is_warm else "base"
        st.caption(
            f"Actual Mar 23: **{actual_ret:+.2f}%** | "
            f"Model ({mode_label}, {total_trees:,} trees): **{full_ret:+.4f}%**"
        )

    # ── Chart — full width ──────────────────────────────────────────────────
    fig = go.Figure()

    pre23 = hist_df[hist_df["trade_date"] < "2026-03-23"]
    on23 = hist_df[hist_df["trade_date"] == "2026-03-23"]

    fig.add_trace(go.Scatter(
        x=pre23["date"], y=pre23["close"],
        mode="lines",
        name="Historical Close",
        line={"color": "#64748b", "width": 2},
    ))

    if not on23.empty:
        if len(pre23):
            fig.add_trace(go.Scatter(
                x=[pre23["date"].iloc[-1], on23["date"].iloc[0]],
                y=[pre23["close"].iloc[-1], on23["close"].iloc[0]],
                mode="lines", showlegend=False,
                line={"color": "#0ea5e9", "width": 2},
            ))

        if is_warm:
            observed = on23.iloc[: current_step + 1]
            fig.add_trace(go.Scatter(
                x=observed["date"], y=observed["close"],
                mode="lines",
                name=f"Observed (0→{step_label})",
                line={"color": "#0ea5e9", "width": 2},
            ))
            remaining = on23.iloc[current_step:]
            if len(remaining) > 1:
                fig.add_trace(go.Scatter(
                    x=remaining["date"], y=remaining["close"],
                    mode="lines",
                    name="Actual — not yet seen",
                    line={"color": "#38bdf8", "width": 2, "dash": "dashdot"},
                    opacity=0.6,
                ))
        else:
            fig.add_trace(go.Scatter(
                x=on23["date"], y=on23["close"],
                mode="lines",
                name="Mar 23 Actual",
                line={"color": "#0ea5e9", "width": 2},
            ))

    bars = pred_active.get("bars", [])
    if bars and not on23.empty:
        if is_warm:
            actual_at_step = float(on23["close"].iloc[current_step])
            base_log = bars[current_step]["pred_log_return"]
            fwd_bars = bars[current_step:]
            fwd_xs = [on23["date"].iloc[current_step + i] for i in range(len(fwd_bars)) if current_step + i < len(on23)]
            fwd_ys = [
                round(actual_at_step * math.exp(b["pred_log_return"] - base_log), 4)
                for b in fwd_bars[: len(fwd_xs)]
            ]
            fig.add_trace(go.Scatter(
                x=fwd_xs, y=fwd_ys,
                mode="lines+markers",
                name=f"Warm Prediction @ {step_label} ({total_trees:,} trees)",
                line={"color": "#f59e0b", "width": 2.5, "dash": "dot"},
                marker={"size": 4, "color": "#f59e0b"},
            ))
        elif anchor_close:
            pred_xs = [on23["date"].iloc[i] for i in range(len(bars)) if i < len(on23)]
            pred_ys = [round(anchor_close * math.exp(b["pred_log_return"]), 4) for b in bars[: len(pred_xs)]]
            fig.add_trace(go.Scatter(
                x=pred_xs, y=pred_ys,
                mode="lines+markers",
                name=f"Base Prediction ({base_trees:,} trees)",
                line={"color": "#f59e0b", "width": 2.5, "dash": "dot"},
                marker={"size": 4, "color": "#f59e0b"},
            ))

    if not on23.empty:
        vline_x = on23["date"].iloc[0].strftime("%Y-%m-%d %H:%M:%S")
        fig.add_shape(
            type="line", x0=vline_x, x1=vline_x, y0=0, y1=1,
            xref="x", yref="paper",
            line={"dash": "dash", "color": "#94a3b8", "width": 1},
        )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="#fcfcfd",
        yaxis_title="Price (USD)",
        xaxis_title=None,
        height=560,
        hovermode="x unified",
        dragmode="pan",
        legend={"orientation": "h", "y": 1.04, "x": 1, "xanchor": "right"},
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        xaxis=dict(
            showgrid=False,
            rangeslider_visible=False,
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
                dict(bounds=[20, 13.5], pattern="hour"),
            ],
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_snapshots() -> None:
    with st.form("build_snapshot"):
        ticker = st.text_input("Ticker", value="ALL", help="Use ALL for every stock.")
        left, right = st.columns(2)
        start_date = left.text_input("Start date", placeholder="YYYY-MM-DD")
        end_date = right.text_input("End date", placeholder="YYYY-MM-DD")
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


# ── Sidebar ────────────────────────────────────────────────────────────────────

def build_sidebar(stocks: list[dict]) -> tuple[str, str | None, int]:
    """Render sidebar branding + all controls. Returns (page, symbol, days)."""
    with st.sidebar:
        # Branding
        st.markdown(
            """
            <div class="sidebar-brand">
                <div style="font-size:1.35rem;font-weight:700;color:#0f172a;line-height:1.1">
                    MarketSight
                </div>
                <div style="font-size:0.75rem;color:#64748b;margin-top:0.3rem;line-height:1.4">
                    Market data, inference &amp; dataset snapshots.<br>
                    Optimized for fast scanning.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation",
            ["Overview", "Stocks", "Predictions", "Simulation", "Snapshots"],
            label_visibility="collapsed",
        )

        st.divider()

        symbol: str | None = None
        days: int = 30

        symbols = [s["symbol"] for s in stocks]
        df = stocks_dataframe(stocks)

        if page in ("Stocks", "Predictions"):
            st.markdown("**Controls**")
            search = st.text_input("Search symbol / company", key="sb_search")
            sectors = ["All"] + sorted([s for s in df["sector"].unique() if s != "N/A"])
            sector_filter = st.selectbox("Sector", sectors, key="sb_sector")

            filtered = df.copy()
            if search:
                m = search.strip().lower()
                filtered = filtered[
                    filtered["symbol"].str.lower().str.contains(m)
                    | filtered["name"].str.lower().str.contains(m)
                ]
            if sector_filter != "All":
                filtered = filtered[filtered["sector"] == sector_filter]

            opts = filtered["symbol"].tolist() if not filtered.empty else symbols
            default = st.session_state.get("selected_symbol", opts[0] if opts else None)
            if default not in opts:
                default = opts[0] if opts else None

            if opts:
                symbol = st.selectbox("Stock", opts, index=opts.index(default) if default in opts else 0, key="sb_symbol")
                st.session_state["selected_symbol"] = symbol

            if page == "Stocks":
                days = st.select_slider(
                    "History window",
                    options=[7, 30, 90, 180, 365, 730],
                    value=st.session_state.get("stocks_days", 30),
                    key="stocks_days",
                )

        elif page == "Simulation":
            st.markdown("**Simulation — 2026-03-23**")
            symbol = st.selectbox(
                "Asset",
                symbols,
                index=symbols.index("AAPL") if "AAPL" in symbols else 0,
                key="sim_symbol",
            )
            st.radio(
                "Prediction view",
                ["Base Model (Mar 20 → Mar 23)", "Warm-Refresh Simulation"],
                horizontal=False,
                key="sim_mode",
            )
            if st.session_state.get("sim_mode") == "Warm-Refresh Simulation":
                try:
                    session_info = load_sim_session()
                    step_count = session_info.get("steps_completed", 26)
                    step_labels = session_info.get("step_labels", [])
                except Exception:
                    step_count = 26
                    step_labels = []

                current_step = st.slider(
                    "Intraday bar",
                    min_value=0,
                    max_value=step_count - 1,
                    value=st.session_state.get("sim_step_slider", 0),
                    key="sim_step_slider",
                    format="%d",
                )
                if step_labels and current_step < len(step_labels):
                    st.caption(f"As of {step_labels[current_step]}")

        st.divider()
        st.caption(f"{datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC")

    return page, symbol, days


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    try:
        stocks = load_stocks()
    except Exception as exc:  # noqa: BLE001
        st.sidebar.error(f"Failed to load stocks: {exc}")
        stocks = []

    page, symbol, days = build_sidebar(stocks)

    if page == "Overview":
        render_overview(stocks)
    elif page == "Stocks":
        render_stocks(stocks, sidebar_symbol=symbol)
    elif page == "Predictions":
        render_predictions(stocks, sidebar_symbol=symbol)
    elif page == "Simulation":
        render_simulation(stocks, sidebar_symbol=symbol)
    else:
        render_snapshots()


if __name__ == "__main__":
    main()
