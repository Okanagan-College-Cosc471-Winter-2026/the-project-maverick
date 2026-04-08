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

st.markdown(
    """
    <style>
    /* Tighten top padding */
    .block-container {padding-top: 1rem; padding-bottom: 0.5rem;}
    /* Sidebar branding block */
    [data-testid="stSidebar"] .sidebar-brand {
        padding: 0.4rem 0 0.9rem 0;
        border-bottom: 1px solid rgba(148,163,184,0.2);
        margin-bottom: 0.6rem;
    }
    /* Make plotly charts not clip at bottom */
    [data-testid="stPlotlyChart"] { overflow: visible !important; }
    /* Reduce gap between elements */
    [data-testid="stVerticalBlock"] > div { gap: 0.4rem; }
    /* Slider: no bottom margin */
    [data-testid="stSlider"] { margin-bottom: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

CHART_H = 580   # chart height in px
TABLE_H = 400


# ── Caches ────────────────────────────────────────────────────────────────────

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


# ── Data helpers ──────────────────────────────────────────────────────────────

def stocks_df(stocks: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(stocks)
    if df.empty:
        return df
    for col in ("sector", "industry", "exchange"):
        if col in df.columns:
            df[col] = df[col].fillna("N/A")
    return df.sort_values("symbol").reset_index(drop=True)

def ohlc_df(symbol: str, days: int) -> pd.DataFrame:
    raw = load_ohlc(symbol, days)
    df = pd.DataFrame(raw)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.sort_values("date").reset_index(drop=True)


# ── Chart builders ────────────────────────────────────────────────────────────

def candlestick_chart(df: pd.DataFrame, title: str, prediction: dict | None = None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="OHLC",
        increasing_line_color="#0f766e", decreasing_line_color="#b91c1c",
        increasing_fillcolor="#14b8a6", decreasing_fillcolor="#ef4444",
    ))
    fig.add_trace(go.Bar(
        x=df["date"], y=df["volume"], name="Volume",
        marker_color="#94a3b8", opacity=0.18, yaxis="y2",
    ))
    if prediction:
        path = prediction.get("path", [])
        if path:
            pred_date = prediction.get("prediction_date", "")[:10]
            px_ = [f"{pred_date} {b['bar_time']}:00" for b in path]
            py_ = [b["pred_close"] for b in path]
            fig.add_trace(go.Scatter(
                x=px_, y=py_, mode="lines+markers", name="Predicted Path",
                line={"color": "#f59e0b", "width": 2, "dash": "dot"},
                marker={"size": 4, "color": "#f59e0b"},
            ))
            fig.add_annotation(
                x=px_[-1], y=py_[-1],
                text=f"EOD ${py_[-1]:.2f}", showarrow=True, arrowhead=2,
                ax=32, ay=-40, bgcolor="rgba(245,158,11,0.12)",
                bordercolor="#f59e0b", font={"size": 11, "color": "#92400e"},
            )
    fig.update_layout(
        title=title, template="plotly_white",
        paper_bgcolor="white", plot_bgcolor="#fcfcfd",
        xaxis_title=None, yaxis_title="Price",
        yaxis2={"title": "Vol", "overlaying": "y", "side": "right", "showgrid": False},
        legend={"orientation": "h", "y": 1.02, "x": 1, "xanchor": "right"},
        margin={"l": 16, "r": 16, "t": 44, "b": 8},
        height=CHART_H, hovermode="x unified", dragmode="pan",
    )
    fig.update_xaxes(
        showgrid=False, rangeslider_visible=False,
        rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=[16, 9.5], pattern="hour")],
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.15)")
    fig.add_hline(y=float(df["close"].iloc[-1]), line_width=1, line_dash="dot", line_color="#94a3b8")
    return fig


def sim_chart(
    hist_df: pd.DataFrame,
    pred_active: dict,
    anchor_close: float | None,
    is_warm: bool,
    current_step: int,
    step_label: str | None,
    base_trees: int,
    total_trees: int,
) -> go.Figure:
    fig = go.Figure()
    pre23 = hist_df[hist_df["trade_date"] < "2026-03-23"]
    on23  = hist_df[hist_df["trade_date"] == "2026-03-23"]

    fig.add_trace(go.Scatter(
        x=pre23["date"], y=pre23["close"], mode="lines",
        name="Historical", line={"color": "#64748b", "width": 2},
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
            obs = on23.iloc[: current_step + 1]
            fig.add_trace(go.Scatter(
                x=obs["date"], y=obs["close"], mode="lines",
                name=f"Observed (→{step_label})",
                line={"color": "#0ea5e9", "width": 2},
            ))
            rest = on23.iloc[current_step:]
            if len(rest) > 1:
                fig.add_trace(go.Scatter(
                    x=rest["date"], y=rest["close"], mode="lines",
                    name="Actual (not seen yet)",
                    line={"color": "#38bdf8", "width": 2, "dash": "dashdot"},
                    opacity=0.55,
                ))
        else:
            fig.add_trace(go.Scatter(
                x=on23["date"], y=on23["close"], mode="lines",
                name="Mar 23 Actual", line={"color": "#0ea5e9", "width": 2},
            ))

    bars = pred_active.get("bars", [])
    if bars and not on23.empty:
        if is_warm:
            actual_at_step = float(on23["close"].iloc[current_step])
            base_log = bars[current_step]["pred_log_return"]
            fwd = bars[current_step:]
            fwd_xs = [on23["date"].iloc[current_step + i] for i in range(len(fwd)) if current_step + i < len(on23)]
            fwd_ys = [round(actual_at_step * math.exp(b["pred_log_return"] - base_log), 4) for b in fwd[:len(fwd_xs)]]
            fig.add_trace(go.Scatter(
                x=fwd_xs, y=fwd_ys, mode="lines+markers",
                name=f"Warm Prediction @ {step_label} ({total_trees:,} trees)",
                line={"color": "#f59e0b", "width": 2.5, "dash": "dot"},
                marker={"size": 4, "color": "#f59e0b"},
            ))
        elif anchor_close:
            xs = [on23["date"].iloc[i] for i in range(len(bars)) if i < len(on23)]
            ys = [round(anchor_close * math.exp(b["pred_log_return"]), 4) for b in bars[:len(xs)]]
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines+markers",
                name=f"Base Prediction ({base_trees:,} trees)",
                line={"color": "#f59e0b", "width": 2.5, "dash": "dot"},
                marker={"size": 4, "color": "#f59e0b"},
            ))

    if not on23.empty:
        vx = on23["date"].iloc[0].strftime("%Y-%m-%d %H:%M:%S")
        fig.add_shape(
            type="line", x0=vx, x1=vx, y0=0, y1=1, xref="x", yref="paper",
            line={"dash": "dash", "color": "#94a3b8", "width": 1},
        )

    fig.update_layout(
        template="plotly_white", paper_bgcolor="white", plot_bgcolor="#fcfcfd",
        yaxis_title="Price (USD)", xaxis_title=None,
        height=CHART_H, hovermode="x unified", dragmode="pan",
        legend={"orientation": "h", "y": 1.03, "x": 1, "xanchor": "right"},
        margin={"l": 16, "r": 16, "t": 30, "b": 8},
        xaxis=dict(
            showgrid=False, rangeslider_visible=False,
            rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=[20, 13.5], pattern="hour")],
        ),
    )
    return fig


# ── Page fragments (only these rerun on widget change inside them) ─────────────

@st.fragment
def stocks_chart_fragment(symbol: str, days: int, detail: dict) -> None:
    """Chart + prediction toggle — reruns in isolation; no page scroll."""
    show_pred = st.toggle("Overlay model prediction", value=False, key=f"pred_toggle_{symbol}")
    prediction = None
    if show_pred:
        with st.spinner("Running inference..."):
            try:
                prediction = predict(symbol)
            except ApiError as exc:
                st.error(str(exc))

    if prediction:
        path = prediction.get("path", [])
        end_price = path[-1]["pred_close"] if path else prediction["current_price"]
        full_ret = prediction.get("predicted_full_day_return", 0.0)
        direction = prediction.get("predicted_direction", "—")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Price", f"${prediction['current_price']:.2f}")
        c2.metric("Predicted EOD", f"${end_price:.2f}")
        c3.metric("Full-Day Return", f"{full_ret:.2f}%",
                  delta=f"{'▲' if direction=='up' else '▼'} {direction}")
        c4.metric("Model", prediction["model_version"])

    df = ohlc_df(symbol, days)
    if df.empty:
        st.warning("No OHLC data available for this symbol.")
        return
    st.plotly_chart(
        candlestick_chart(df, f"{detail.get('name', symbol)} ({symbol})", prediction),
        use_container_width=True,
    )

    info_tab, data_tab = st.tabs(["Summary", "Raw Data"])
    with info_tab:
        c1, c2 = st.columns(2)
        c1.write(f"**Sector:** {detail.get('sector') or 'N/A'}")
        c1.write(f"**Industry:** {detail.get('industry') or 'N/A'}")
        c1.write(f"**Exchange:** {detail.get('exchange') or 'N/A'}")
        c2.write(f"**High:** ${float(df['high'].max()):.2f}")
        c2.write(f"**Low:** ${float(df['low'].min()):.2f}")
        c2.write(f"**Latest Vol:** {int(df['volume'].iloc[-1]):,}")
    with data_tab:
        raw = df[["date","open","high","low","close","volume"]].tail(200).sort_values("date", ascending=False)
        st.dataframe(raw, use_container_width=True, hide_index=True, height=360,
            column_config={
                "date": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm"),
                "open": st.column_config.NumberColumn("Open", format="$%.2f"),
                "high": st.column_config.NumberColumn("High", format="$%.2f"),
                "low": st.column_config.NumberColumn("Low", format="$%.2f"),
                "close": st.column_config.NumberColumn("Close", format="$%.2f"),
                "volume": st.column_config.NumberColumn("Volume", format="%d"),
            })


@st.fragment
def sim_fragment(
    symbol: str,
    hist_df: pd.DataFrame,
    pred_base: dict,
    session_info: dict,
    anchor_close: float | None,
    actual_ret: float | None,
) -> None:
    """Slider + chart in one fragment — dragging never scrolls the page."""
    step_labels: list[str] = session_info.get("step_labels", [])
    step_count: int = session_info.get("steps_completed", 26)
    base_trees: int = session_info.get("base_trees", 1157)
    warm_per_step: int = session_info.get("warm_trees_per_step", 30)

    is_warm = st.session_state.get("sim_mode") == "Warm-Refresh Simulation"

    pred_active = pred_base
    current_step = 0
    step_label: str | None = None
    total_trees = base_trees

    if is_warm:
        current_step = st.slider(
            "Intraday bar (drag to step through warm-refresh)",
            min_value=0, max_value=step_count - 1, value=0,
            key="sim_step_slider",
            help="Each step adds warm-refresh trees trained on bars observed so far.",
        )
        step_label = step_labels[current_step] if current_step < len(step_labels) else str(current_step)
        total_trees = base_trees + (current_step + 1) * warm_per_step
        with st.spinner(f"Loading step {step_label}…"):
            try:
                pred_active = load_sim_step(symbol, current_step)
            except ApiError as exc:
                st.error(str(exc))
                return

    # Metrics
    full_ret = pred_active.get("predicted_full_day_return", 0.0)
    direction = pred_active.get("predicted_direction", "—")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Base Trained", "2026-03-20")
    c2.metric("Target Date", "2026-03-23")
    c3.metric("Predicted Return", f"{full_ret:+.4f}%")
    c4.metric("Direction", direction.upper())
    if actual_ret is not None:
        label = f"step {current_step} ({step_label}), {total_trees:,} trees" if is_warm else f"base, {base_trees:,} trees"
        st.caption(f"Actual Mar 23: **{actual_ret:+.2f}%** | Model ({label}): **{full_ret:+.4f}%**")

    # Chart
    fig = sim_chart(
        hist_df, pred_active, anchor_close, is_warm,
        current_step, step_label, base_trees, total_trees,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Pages ──────────────────────────────────────────────────────────────────────

def render_overview(stocks: list[dict]) -> None:
    st.subheader("Overview")
    try:
        healthy = health_check()
        health_error = None
    except Exception as exc:  # noqa: BLE001
        healthy = False
        health_error = str(exc)

    df = stocks_df(stocks)
    sectors = sorted({s["sector"] for s in stocks if s.get("sector") and s["sector"] != "N/A"})

    c1, c2, c3 = st.columns(3)
    c1.metric("Tracked Stocks", len(stocks))
    c2.metric("Sectors", len(sectors))
    c3.metric("API Status", "Online" if healthy else "Unavailable")
    if health_error:
        st.warning(f"Health check failed: {health_error}")

    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("#### Coverage")
        st.dataframe(
            df[["symbol","name","sector","exchange"]],
            use_container_width=True, hide_index=True, height=460,
            column_config={
                "symbol": st.column_config.TextColumn("Symbol", width="small"),
                "name": st.column_config.TextColumn("Company", width="medium"),
                "sector": st.column_config.TextColumn("Sector", width="medium"),
                "exchange": st.column_config.TextColumn("Exchange", width="small"),
            },
        )
    with right:
        st.markdown("#### Sector Breakdown")
        if sectors:
            sector_counts = df[df["sector"] != "N/A"]["sector"].value_counts()
            st.bar_chart(sector_counts)
        else:
            st.info("No sector metadata available.")


def render_stocks(stocks: list[dict], symbol: str, days: int) -> None:
    if not stocks:
        st.info("No stocks available.")
        return
    detail = next((s for s in stocks if s["symbol"] == symbol), {})

    # Top metrics (outside fragment — only reruns when symbol/days change)
    df = ohlc_df(symbol, days)
    if not df.empty:
        latest = float(df["close"].iloc[-1])
        first  = float(df["close"].iloc[0])
        period_ret = ((latest / first) - 1) * 100 if first else 0.0
        avg_vol = float(df["volume"].tail(20).mean())
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Close", f"${latest:.2f}")
        c2.metric("Period Return", f"{period_ret:.2f}%")
        c3.metric("Avg Vol (20)", f"{int(avg_vol):,}")
        c4.metric("Bars", f"{len(df):,}")

    # Fragment handles prediction toggle + chart (no scroll on toggle)
    stocks_chart_fragment(symbol, days, detail)


def render_predictions(stocks: list[dict], symbol: str) -> None:
    if not stocks:
        st.info("No stocks available.")
        return
    if st.button("Generate Prediction", type="primary"):
        with st.spinner("Running inference…"):
            try:
                payload = predict(symbol)
            except ApiError as exc:
                st.error(str(exc))
                return
        path = payload.get("path", [])
        end_price = path[-1]["pred_close"] if path else payload["current_price"]
        full_ret = payload.get("predicted_full_day_return", 0.0)
        direction = payload.get("predicted_direction", "—")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Price", f"${payload['current_price']:.2f}")
        c2.metric("Predicted EOD", f"${end_price:.2f}")
        c3.metric("Return", f"{full_ret:.2f}%",
                  delta=f"{'▲' if direction=='up' else '▼'} {direction}")
        c4.metric("Model", payload["model_version"])

        df = ohlc_df(symbol, 365)
        if not df.empty:
            st.plotly_chart(
                candlestick_chart(df, f"{symbol} — Predicted Path", payload),
                use_container_width=True,
            )
        st.caption(f"26-bar 15-min path for {payload['prediction_date'][:10]}.")


def render_simulation(stocks: list[dict], symbol: str) -> None:
    try:
        session_info = load_sim_session()
    except ApiError as exc:
        st.error(f"Could not load session info: {exc}")
        return

    try:
        hist_raw = load_sim_history(symbol)
        hist = pd.DataFrame(hist_raw)
        hist["date"] = pd.to_datetime(hist["time"], unit="s", utc=True)
        hist = hist.sort_values("date").reset_index(drop=True)
    except ApiError as exc:
        st.error(f"Could not load history: {exc}")
        return

    mar20 = hist[hist["trade_date"] == "2026-03-20"]
    anchor_close = float(mar20["close"].iloc[-1]) if not mar20.empty else None

    mar23 = hist[hist["trade_date"] == "2026-03-23"]
    actual_ret = None
    if not mar23.empty:
        actual_ret = (float(mar23["close"].iloc[-1]) / float(mar23["close"].iloc[0]) - 1) * 100

    try:
        pred_base = load_sim_base(symbol)
    except ApiError as exc:
        st.error(f"Base prediction failed: {exc}")
        return

    # Fragment owns the slider + chart — no full-page reruns when dragging
    sim_fragment(symbol, hist, pred_base, session_info, anchor_close, actual_ret)


def render_snapshots() -> None:
    with st.form("build_snapshot"):
        ticker = st.text_input("Ticker", value="ALL", help="Use ALL for every stock.")
        left, right = st.columns(2)
        start_date = left.text_input("Start date", placeholder="YYYY-MM-DD")
        end_date   = right.text_input("End date",   placeholder="YYYY-MM-DD")
        file_format = st.selectbox("Format", ["parquet", "csv", "both"])
        submitted = st.form_submit_button("Build Snapshot", type="primary")

    if submitted:
        with st.spinner("Building…"):
            try:
                result = build_snapshot({
                    "ticker": ticker or "ALL",
                    "start_date": start_date or None,
                    "end_date": end_date or None,
                    "format": file_format,
                })
            except ApiError as exc:
                st.error(str(exc))
            else:
                st.success(f"Created for {result['tickers_processed']} ticker(s), {result['total_rows_extracted']} rows.")
                st.json(result, expanded=False)
                load_snapshots.clear()

    try:
        payload = load_snapshots()
    except ApiError as exc:
        st.error(str(exc))
        return

    snapshots = payload.get("snapshots", [])
    st.caption(f"Directory: {payload.get('directory', '—')}")
    if not snapshots:
        st.info("No snapshots yet.")
        return

    df = pd.DataFrame(snapshots).sort_values("filename").reset_index(drop=True)
    st.dataframe(df, use_container_width=True, hide_index=True, height=TABLE_H,
        column_config={
            "filename": st.column_config.TextColumn("File", width="large"),
            "size_mb": st.column_config.NumberColumn("Size (MB)", format="%.2f"),
        })

    selected = st.selectbox("Download", df["filename"].tolist())
    if st.button("Prepare Download"):
        with st.spinner("Fetching…"):
            try:
                file_obj = download_snapshot(selected)
            except ApiError as exc:
                st.error(str(exc))
                return
        st.download_button(f"Download {selected}", file_obj.getvalue(),
                           file_name=selected, mime="application/octet-stream")


# ── Sidebar ────────────────────────────────────────────────────────────────────

def build_sidebar(stocks: list[dict]) -> tuple[str, str, int]:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div style="font-size:1.3rem;font-weight:700;color:#0f172a;line-height:1.1">
                    MarketSight
                </div>
                <div style="font-size:0.72rem;color:#64748b;margin-top:0.25rem;line-height:1.45">
                    Market data, inference &amp; dataset snapshots.<br>
                    Optimized for fast scanning.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation", ["Overview","Stocks","Predictions","Simulation","Snapshots"],
            label_visibility="collapsed",
        )
        st.divider()

        df = stocks_df(stocks)
        symbols = df["symbol"].tolist() if not df.empty else []
        symbol = symbols[0] if symbols else ""
        days = 30

        if page in ("Stocks", "Predictions"):
            st.markdown("**Controls**")
            search = st.text_input("Search", placeholder="symbol or company", label_visibility="collapsed")
            sectors = ["All"] + sorted([s for s in df["sector"].unique() if s != "N/A"])
            sector_filter = st.selectbox("Sector", sectors)

            filtered = df.copy()
            if search:
                m = search.strip().lower()
                filtered = filtered[
                    filtered["symbol"].str.lower().str.contains(m, na=False)
                    | filtered["name"].str.lower().str.contains(m, na=False)
                ]
            if sector_filter != "All":
                filtered = filtered[filtered["sector"] == sector_filter]

            opts = filtered["symbol"].tolist() if not filtered.empty else symbols
            default = st.session_state.get("selected_symbol", opts[0] if opts else "")
            if default not in opts:
                default = opts[0] if opts else ""

            if opts:
                symbol = st.selectbox("Stock", opts,
                    index=opts.index(default) if default in opts else 0,
                    key="sb_symbol")
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
            default_sym = "AAPL" if "AAPL" in symbols else (symbols[0] if symbols else "")
            symbol = st.selectbox("Asset", symbols,
                index=symbols.index(default_sym) if default_sym in symbols else 0,
                key="sim_symbol")
            st.radio(
                "Mode",
                ["Base Model (Mar 20 → Mar 23)", "Warm-Refresh Simulation"],
                key="sim_mode",
            )
            # Step slider lives inside the fragment (main area) so dragging it
            # only reruns the fragment — no sidebar needed here.

        st.divider()
        st.caption(f"{datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC")

    return page, symbol, days


# ── Entry point ───────────────────────────────────────────────────────────────

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
        render_stocks(stocks, symbol, days)
    elif page == "Predictions":
        render_predictions(stocks, symbol)
    elif page == "Simulation":
        render_simulation(stocks, symbol)
    else:
        render_snapshots()


if __name__ == "__main__":
    main()
