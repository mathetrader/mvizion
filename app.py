import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime, date, timedelta
import io
import os

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="mVizion · Trading Journal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0a0c10;
    --bg2: #111318;
    --bg3: #181c24;
    --border: #232836;
    --accent1: #4fffb0;
    --accent2: #7c6fff;
    --accent3: #ff6b6b;
    --accent4: #ffd166;
    --text: #e8eaf0;
    --muted: #6b7280;
    --green: #22c55e;
    --red: #ef4444;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Main bg */
.main { background: var(--bg) !important; }
.block-container { padding: 1.5rem 2rem !important; }

/* Cards */
.card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color .2s;
}
.card:hover { border-color: var(--accent2); }

/* KPI */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, var(--accent1), var(--accent2));
}
.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .1em;
    margin-bottom: .4rem;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: .3rem;
}
.green { color: var(--accent1) !important; }
.red   { color: var(--accent3) !important; }
.gold  { color: var(--accent4) !important; }
.purple{ color: var(--accent2) !important; }

/* Table */
.trade-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}
.trade-table th {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: var(--muted);
    padding: .7rem 1rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
}
.trade-table td {
    padding: .65rem 1rem;
    border-bottom: 1px solid #1a1f2a;
    color: var(--text);
}
.trade-table tr:hover td { background: var(--bg3); }

.badge {
    display: inline-block;
    padding: .2rem .6rem;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}
.badge-long  { background: rgba(78,255,176,.15); color: var(--accent1); }
.badge-short { background: rgba(255,107,107,.15); color: var(--accent3); }
.badge-win   { background: rgba(78,255,176,.12); color: var(--accent1); }
.badge-loss  { background: rgba(255,107,107,.12); color: var(--accent3); }

/* Inputs */
input, select, textarea, [data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input, [data-testid="stSelectbox"] select {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, var(--accent1), var(--accent2)) !important;
    color: #0a0c10 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: .5rem 1.5rem !important;
    transition: opacity .2s !important;
}
.stButton button:hover { opacity: .85 !important; }

/* Title */
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent1), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.page-subtitle {
    font-size: .85rem;
    color: var(--muted);
    margin-bottom: 1.5rem;
}

/* Logo */
.logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent1), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Hide streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg3) !important;
    color: var(--text) !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
}
[data-testid="metric-container"] label { color: var(--muted) !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--bg3) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 12px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent2); }

</style>
""", unsafe_allow_html=True)


# ─── Data helpers ────────────────────────────────────────────────────────────
def init_state():
    if "trades" not in st.session_state:
        st.session_state.trades = []
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

def trades_df():
    if not st.session_state.trades:
        return pd.DataFrame()
    df = pd.DataFrame(st.session_state.trades)
    df["date"] = pd.to_datetime(df["date"])
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
    df["rr"] = pd.to_numeric(df["rr"], errors="coerce")
    df.sort_values("date", ascending=False, inplace=True)
    return df

def save_trades_json():
    return json.dumps(st.session_state.trades, default=str, indent=2)

def load_trades_json(data):
    st.session_state.trades = json.loads(data)

def parse_tradingview_csv(df_raw):
    """Try to map TradingView CSV columns to our schema."""
    col_map = {
        "Trade #": "id",
        "Symbol": "symbol",
        "Type": "direction",
        "Entry": "entry",
        "Exit": "exit",
        "Profit": "pnl",
        "Date/Time": "date",
        "Qty": "qty",
    }
    # Flexible mapping
    mapped = {}
    for src, dst in col_map.items():
        for c in df_raw.columns:
            if src.lower() in c.lower():
                mapped[dst] = c
                break

    trades_out = []
    for _, row in df_raw.iterrows():
        t = {
            "id": str(len(st.session_state.trades) + len(trades_out) + 1),
            "symbol": str(row.get(mapped.get("symbol", ""), "UNKNOWN")),
            "direction": "Long" if "long" in str(row.get(mapped.get("direction", ""), "")).lower() else "Short",
            "entry": float(str(row.get(mapped.get("entry", ""), 0)).replace(",", ".") or 0),
            "exit": float(str(row.get(mapped.get("exit", ""), 0)).replace(",", ".") or 0),
            "qty": float(str(row.get(mapped.get("qty", ""), 1)).replace(",", ".") or 1),
            "pnl": float(str(row.get(mapped.get("pnl", ""), 0)).replace(",", "").replace(" ", "") or 0),
            "date": str(row.get(mapped.get("date", ""), datetime.now().date())),
            "rr": 0.0,
            "setup": "Import TV",
            "notes": "",
            "screenshot": "",
            "session": "London",
            "result": "",
        }
        t["result"] = "Win" if t["pnl"] > 0 else "Loss"
        trades_out.append(t)
    return trades_out


# ─── KPI calculations ────────────────────────────────────────────────────────
def compute_kpis(df):
    if df.empty:
        return {"total_pnl": 0, "win_rate": 0, "total_trades": 0, "avg_rr": 0,
                "best_trade": 0, "worst_trade": 0, "profit_factor": 0, "streak": 0}
    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] <= 0]
    total_pnl = df["pnl"].sum()
    win_rate = len(wins) / len(df) * 100 if len(df) > 0 else 0
    avg_rr = df["rr"].mean() if "rr" in df.columns else 0
    gross_profit = wins["pnl"].sum() if not wins.empty else 0
    gross_loss = abs(losses["pnl"].sum()) if not losses.empty else 1
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
    # streak
    results = df.sort_values("date")["pnl"].tolist()
    streak, cur = 0, 0
    for p in reversed(results):
        if (p > 0 and cur >= 0) or (p <= 0 and cur <= 0):
            cur += 1 if p > 0 else -1
        else:
            break
    streak = cur
    return {
        "total_pnl": total_pnl,
        "win_rate": win_rate,
        "total_trades": len(df),
        "avg_rr": avg_rr if not np.isnan(avg_rr) else 0,
        "best_trade": df["pnl"].max(),
        "worst_trade": df["pnl"].min(),
        "profit_factor": profit_factor,
        "streak": streak,
    }


# ─── Charts ──────────────────────────────────────────────────────────────────
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e8eaf0",
    font_family="Plus Jakarta Sans",
    xaxis=dict(gridcolor="#1e2330", zerolinecolor="#1e2330"),
    yaxis=dict(gridcolor="#1e2330", zerolinecolor="#1e2330"),
    margin=dict(l=10, r=10, t=30, b=10),
)

def chart_equity(df):
    df2 = df.sort_values("date").copy()
    df2["cumulative"] = df2["pnl"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df2["date"], y=df2["cumulative"],
        mode="lines", name="Equity",
        line=dict(color="#4fffb0", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(78,255,176,0.07)"
    ))
    fig.update_layout(**CHART_THEME, height=280, title="Courbe d'équité")
    return fig

def chart_pnl_bar(df):
    df2 = df.sort_values("date").copy()
    colors = ["#4fffb0" if p > 0 else "#ff6b6b" for p in df2["pnl"]]
    fig = go.Figure(go.Bar(
        x=df2["date"], y=df2["pnl"],
        marker_color=colors,
        name="P&L"
    ))
    fig.update_layout(**CHART_THEME, height=240, title="P&L par trade")
    return fig

def chart_winrate_donut(kpis):
    fig = go.Figure(go.Pie(
        values=[kpis["win_rate"], 100 - kpis["win_rate"]],
        labels=["Wins", "Losses"],
        hole=0.72,
        marker_colors=["#4fffb0", "#ff6b6b"],
        textinfo="none",
    ))
    fig.update_layout(
        **CHART_THEME,
        height=220,
        showlegend=False,
        annotations=[dict(text=f"{kpis['win_rate']:.0f}%", x=0.5, y=0.5,
                          font=dict(size=26, color="#e8eaf0", family="Syne"), showarrow=False)]
    )
    return fig

def chart_monthly(df):
    df2 = df.copy()
    df2["month"] = df2["date"].dt.to_period("M").astype(str)
    monthly = df2.groupby("month")["pnl"].sum().reset_index()
    colors = ["#4fffb0" if p > 0 else "#ff6b6b" for p in monthly["pnl"]]
    fig = go.Figure(go.Bar(x=monthly["month"], y=monthly["pnl"], marker_color=colors))
    fig.update_layout(**CHART_THEME, height=240, title="P&L Mensuel")
    return fig

def chart_symbol_perf(df):
    sym = df.groupby("symbol")["pnl"].sum().sort_values().reset_index()
    colors = ["#4fffb0" if p > 0 else "#ff6b6b" for p in sym["pnl"]]
    fig = go.Figure(go.Bar(x=sym["pnl"], y=sym["symbol"], orientation="h", marker_color=colors))
    fig.update_layout(**CHART_THEME, height=260, title="Performance par symbole")
    return fig

def chart_session(df):
    if "session" not in df.columns:
        return None
    sess = df.groupby("session")["pnl"].sum().reset_index()
    fig = go.Figure(go.Bar(x=sess["session"], y=sess["pnl"],
                           marker_color=["#7c6fff", "#4fffb0", "#ffd166"]))
    fig.update_layout(**CHART_THEME, height=220, title="P&L par session")
    return fig


# ─── Sidebar ─────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown('<div class="logo">m<span style="color:#e8eaf0">Vizion</span></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.72rem;color:#6b7280;margin-bottom:1.5rem;font-family:\'DM Mono\',monospace;">TRADING JOURNAL · INDICES</div>', unsafe_allow_html=True)
        st.markdown("---")

        pages = ["📊 Dashboard", "📋 Journal", "➕ Ajouter Trade", "📥 Import CSV", "💾 Données"]
        icons = ["📊", "📋", "➕", "📥", "💾"]
        labels = ["Dashboard", "Journal", "Ajouter Trade", "Import CSV", "Données"]

        for icon, label in zip(icons, labels):
            active = st.session_state.page == label
            style = "background:linear-gradient(135deg,rgba(78,255,176,.1),rgba(124,111,255,.1));border-left:2px solid #4fffb0;" if active else "border-left:2px solid transparent;"
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.rerun()

        st.markdown("---")
        df = trades_df()
        if not df.empty:
            kpis = compute_kpis(df)
            color = "#4fffb0" if kpis["total_pnl"] >= 0 else "#ff6b6b"
            sign = "+" if kpis["total_pnl"] >= 0 else ""
            st.markdown(f"""
            <div style="background:var(--bg3);border-radius:12px;padding:1rem;border:1px solid var(--border)">
                <div style="font-size:.68rem;color:#6b7280;font-family:'DM Mono',monospace;text-transform:uppercase;margin-bottom:.5rem;">RÉSUMÉ</div>
                <div style="color:{color};font-size:1.3rem;font-family:'Syne',sans-serif;font-weight:800;">{sign}{kpis['total_pnl']:,.2f}€</div>
                <div style="font-size:.75rem;color:#6b7280;margin-top:.3rem;">{kpis['total_trades']} trades · {kpis['win_rate']:.0f}% WR</div>
            </div>
            """, unsafe_allow_html=True)


# ─── Pages ───────────────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Vue d\'ensemble de tes performances de trading</div>', unsafe_allow_html=True)

    df = trades_df()
    if df.empty:
        st.info("💡 Aucun trade enregistré. Commence par **Ajouter Trade** ou **Import CSV**.")
        return

    kpis = compute_kpis(df)

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sign = "+" if kpis["total_pnl"] >= 0 else ""
        color = "green" if kpis["total_pnl"] >= 0 else "red"
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">P&L Total</div>
            <div class="kpi-value {color}">{sign}{kpis['total_pnl']:,.2f}€</div>
            <div class="kpi-sub">{kpis['total_trades']} trades</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Win Rate</div>
            <div class="kpi-value purple">{kpis['win_rate']:.1f}%</div>
            <div class="kpi-sub">objectif ≥ 55%</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        pf_color = "green" if kpis["profit_factor"] >= 1 else "red"
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Profit Factor</div>
            <div class="kpi-value {pf_color}">{kpis['profit_factor']:.2f}</div>
            <div class="kpi-sub">objectif ≥ 1.5</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        streak_color = "green" if kpis["streak"] > 0 else "red"
        streak_label = f"+{kpis['streak']} wins" if kpis["streak"] > 0 else f"{kpis['streak']} losses"
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Série en cours</div>
            <div class="kpi-value {streak_color}">{streak_label}</div>
            <div class="kpi-sub">Avg R:R {kpis['avg_rr']:.2f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 1
    col1, col2 = st.columns([2.5, 1])
    with col1:
        st.plotly_chart(chart_equity(df), use_container_width=True, config={"displayModeBar": False})
    with col2:
        st.markdown('<div style="text-align:center;padding-top:.5rem;font-size:.75rem;color:#6b7280;font-family:\'DM Mono\',monospace;text-transform:uppercase;margin-bottom:.5rem;">Win Rate</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_winrate_donut(kpis), use_container_width=True, config={"displayModeBar": False})

    # Charts row 2
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(chart_pnl_bar(df), use_container_width=True, config={"displayModeBar": False})
    with col4:
        st.plotly_chart(chart_monthly(df), use_container_width=True, config={"displayModeBar": False})

    # Charts row 3
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(chart_symbol_perf(df), use_container_width=True, config={"displayModeBar": False})
    with col6:
        sc = chart_session(df)
        if sc:
            st.plotly_chart(sc, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="card" style="height:220px;display:flex;align-items:center;justify-content:center;color:#6b7280;">Pas de données de session</div>', unsafe_allow_html=True)

    # Best/Worst
    st.markdown("<br>", unsafe_allow_html=True)
    c_b, c_w = st.columns(2)
    with c_b:
        best = df.loc[df["pnl"].idxmax()]
        st.markdown(f"""<div class="card">
            <div class="kpi-label">🏆 Meilleur Trade</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#4fffb0;">+{best['pnl']:,.2f}€</div>
            <div style="color:#6b7280;font-size:.8rem;margin-top:.3rem;">{best['symbol']} · {str(best['date'])[:10]}</div>
        </div>""", unsafe_allow_html=True)
    with c_w:
        worst = df.loc[df["pnl"].idxmin()]
        st.markdown(f"""<div class="card">
            <div class="kpi-label">📉 Pire Trade</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#ff6b6b;">{worst['pnl']:,.2f}€</div>
            <div style="color:#6b7280;font-size:.8rem;margin-top:.3rem;">{worst['symbol']} · {str(worst['date'])[:10]}</div>
        </div>""", unsafe_allow_html=True)


def page_journal():
    st.markdown('<div class="page-title">Journal des Trades</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Historique complet de tes positions</div>', unsafe_allow_html=True)

    df = trades_df()
    if df.empty:
        st.info("Aucun trade pour l'instant.")
        return

    # Filters
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        symbols = ["Tous"] + sorted(df["symbol"].unique().tolist())
        sym_filter = st.selectbox("Symbole", symbols)
    with fc2:
        dir_filter = st.selectbox("Direction", ["Tous", "Long", "Short"])
    with fc3:
        res_filter = st.selectbox("Résultat", ["Tous", "Win", "Loss"])
    with fc4:
        setup_list = ["Tous"] + sorted(df["setup"].unique().tolist()) if "setup" in df.columns else ["Tous"]
        setup_filter = st.selectbox("Setup", setup_list)

    df_f = df.copy()
    if sym_filter != "Tous":
        df_f = df_f[df_f["symbol"] == sym_filter]
    if dir_filter != "Tous":
        df_f = df_f[df_f["direction"] == dir_filter]
    if res_filter != "Tous":
        df_f = df_f[df_f["result"] == res_filter]
    if setup_filter != "Tous" and "setup" in df_f.columns:
        df_f = df_f[df_f["setup"] == setup_filter]

    st.markdown(f'<div style="color:#6b7280;font-size:.8rem;margin-bottom:.8rem;">{len(df_f)} trade(s) affiché(s)</div>', unsafe_allow_html=True)

    # Table header
    header = """<table class="trade-table">
    <thead><tr>
        <th>Date</th><th>Symbole</th><th>Direction</th>
        <th>Entrée</th><th>Sortie</th><th>Qté</th>
        <th>P&L</th><th>R:R</th><th>Setup</th><th>Résultat</th><th>Notes</th>
    </tr></thead><tbody>"""

    rows = ""
    for _, t in df_f.iterrows():
        pnl_color = "#4fffb0" if float(t["pnl"]) > 0 else "#ff6b6b"
        sign = "+" if float(t["pnl"]) > 0 else ""
        dir_badge = f'<span class="badge badge-long">Long</span>' if t["direction"] == "Long" else f'<span class="badge badge-short">Short</span>'
        res_badge = f'<span class="badge badge-win">Win</span>' if t.get("result") == "Win" else f'<span class="badge badge-loss">Loss</span>'
        notes = str(t.get("notes", ""))[:40] + "..." if len(str(t.get("notes", ""))) > 40 else str(t.get("notes", ""))
        rows += f"""<tr>
            <td style="font-family:'DM Mono',monospace;font-size:.78rem;">{str(t['date'])[:10]}</td>
            <td style="font-weight:600;">{t['symbol']}</td>
            <td>{dir_badge}</td>
            <td style="font-family:'DM Mono',monospace;">{float(t['entry']):.2f}</td>
            <td style="font-family:'DM Mono',monospace;">{float(t['exit']):.2f}</td>
            <td style="font-family:'DM Mono',monospace;">{float(t.get('qty', 1)):.2f}</td>
            <td style="font-family:'DM Mono',monospace;color:{pnl_color};font-weight:600;">{sign}{float(t['pnl']):.2f}€</td>
            <td style="font-family:'DM Mono',monospace;">{float(t.get('rr', 0)):.2f}</td>
            <td style="font-size:.78rem;color:#7c6fff;">{t.get('setup','')}</td>
            <td>{res_badge}</td>
            <td style="font-size:.75rem;color:#6b7280;">{notes}</td>
        </tr>"""

    st.markdown(header + rows + "</tbody></table>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Delete trade
    with st.expander("🗑️ Supprimer un trade"):
        trade_ids = [f"#{t['id']} · {t['symbol']} · {str(t['date'])[:10]}" for t in st.session_state.trades]
        if trade_ids:
            to_delete = st.selectbox("Trade à supprimer", trade_ids)
            if st.button("Supprimer"):
                idx = trade_ids.index(to_delete)
                st.session_state.trades.pop(idx)
                st.success("Trade supprimé !")
                st.rerun()


def page_add_trade():
    st.markdown('<div class="page-title">Ajouter un Trade</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enregistre manuellement une nouvelle position</div>', unsafe_allow_html=True)

    with st.form("add_trade_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            symbol = st.text_input("Symbole", placeholder="CAC40, SP500, NQ...")
            direction = st.selectbox("Direction", ["Long", "Short"])
            session = st.selectbox("Session", ["London", "New York", "Asian", "Pre-market"])
        with c2:
            trade_date = st.date_input("Date", value=date.today())
            entry = st.number_input("Prix d'entrée", min_value=0.0, format="%.4f")
            exit_p = st.number_input("Prix de sortie", min_value=0.0, format="%.4f")
        with c3:
            qty = st.number_input("Quantité / Lots", min_value=0.01, value=1.0, format="%.2f")
            pnl = st.number_input("P&L (€)", format="%.2f")
            rr = st.number_input("Risk:Reward", min_value=0.0, value=0.0, format="%.2f")

        c4, c5 = st.columns(2)
        with c4:
            setup = st.text_input("Setup", placeholder="BOS, FVG, OB, ICT...")
        with c5:
            result = st.selectbox("Résultat", ["Win", "Loss", "Breakeven"])

        notes = st.text_area("Notes / Analyse", placeholder="Décris ton setup, ton raisonnement...", height=100)

        submitted = st.form_submit_button("💾 Enregistrer le Trade", use_container_width=True)
        if submitted:
            if not symbol:
                st.error("Le symbole est obligatoire.")
            else:
                trade = {
                    "id": str(len(st.session_state.trades) + 1),
                    "symbol": symbol.upper(),
                    "direction": direction,
                    "date": str(trade_date),
                    "entry": float(entry),
                    "exit": float(exit_p),
                    "qty": float(qty),
                    "pnl": float(pnl),
                    "rr": float(rr),
                    "setup": setup,
                    "result": result,
                    "session": session,
                    "notes": notes,
                }
                st.session_state.trades.append(trade)
                st.success(f"✅ Trade {symbol.upper()} enregistré avec succès !")
                st.balloons()


def page_import():
    st.markdown('<div class="page-title">Import CSV TradingView</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Importe tes trades depuis TradingView ou un fichier CSV standard</div>', unsafe_allow_html=True)

    # Instructions
    with st.expander("📖 Comment exporter depuis TradingView ?"):
        st.markdown("""
        1. Ouvre ton **Strategy Tester** sur TradingView
        2. Clique sur l'onglet **"Liste des trades"**
        3. Clique sur **"Exporter les données"** (icône ↓)
        4. Sauvegarde le fichier CSV
        5. Importe-le ici !

        **Colonnes supportées :** Trade #, Symbol, Type, Entry, Exit, Profit, Date/Time, Qty
        """)

    tab1, tab2 = st.tabs(["📂 Import Fichier", "📋 Coller CSV"])

    with tab1:
        uploaded = st.file_uploader("Dépose ton fichier CSV ici", type=["csv"])
        sep = st.selectbox("Séparateur", [",", ";", "\t"], index=0)

        if uploaded:
            try:
                df_raw = pd.read_csv(uploaded, sep=sep)
                st.markdown(f'<div style="color:#4fffb0;margin-bottom:.5rem;">✅ {len(df_raw)} lignes détectées</div>', unsafe_allow_html=True)
                st.dataframe(df_raw.head(5), use_container_width=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🚀 Importer (auto-mapping TradingView)", use_container_width=True):
                        new_trades = parse_tradingview_csv(df_raw)
                        st.session_state.trades.extend(new_trades)
                        st.success(f"✅ {len(new_trades)} trades importés !")
                        st.rerun()

            except Exception as e:
                st.error(f"Erreur de lecture : {e}")

    with tab2:
        csv_text = st.text_area("Colle le contenu CSV ici", height=200,
                                placeholder="Trade #,Symbol,Type,Entry,Exit,Profit,Date/Time\n1,CAC40,Long,7500,7580,80,2024-01-15")
        if st.button("📤 Importer le texte") and csv_text:
            try:
                df_raw = pd.read_csv(io.StringIO(csv_text))
                new_trades = parse_tradingview_csv(df_raw)
                st.session_state.trades.extend(new_trades)
                st.success(f"✅ {len(new_trades)} trades importés !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

    st.markdown("---")
    st.markdown("### 📥 Mapping manuel des colonnes")
    st.markdown('<div style="color:#6b7280;font-size:.83rem;">Si tes colonnes ont des noms différents, utilise le mapping manuel ci-dessous.</div>', unsafe_allow_html=True)

    uploaded2 = st.file_uploader("Fichier CSV (mapping manuel)", type=["csv"], key="manual_csv")
    if uploaded2:
        df_raw2 = pd.read_csv(uploaded2)
        cols = list(df_raw2.columns)
        st.dataframe(df_raw2.head(3), use_container_width=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            col_sym = st.selectbox("Symbole", ["—"] + cols)
            col_dir = st.selectbox("Direction", ["—"] + cols)
        with m2:
            col_date = st.selectbox("Date", ["—"] + cols)
            col_entry = st.selectbox("Entrée", ["—"] + cols)
        with m3:
            col_exit = st.selectbox("Sortie", ["—"] + cols)
            col_pnl = st.selectbox("P&L", ["—"] + cols)
        with m4:
            col_qty = st.selectbox("Quantité", ["—"] + cols)
            col_rr = st.selectbox("R:R", ["—"] + cols)

        if st.button("✅ Importer avec ce mapping"):
            new_trades = []
            for _, row in df_raw2.iterrows():
                t = {
                    "id": str(len(st.session_state.trades) + len(new_trades) + 1),
                    "symbol": str(row[col_sym]) if col_sym != "—" else "UNKNOWN",
                    "direction": str(row[col_dir]) if col_dir != "—" else "Long",
                    "date": str(row[col_date]) if col_date != "—" else str(date.today()),
                    "entry": float(str(row[col_entry]).replace(",", ".") or 0) if col_entry != "—" else 0,
                    "exit": float(str(row[col_exit]).replace(",", ".") or 0) if col_exit != "—" else 0,
                    "qty": float(str(row[col_qty]).replace(",", ".") or 1) if col_qty != "—" else 1,
                    "pnl": float(str(row[col_pnl]).replace(",", "").replace(" ", "") or 0) if col_pnl != "—" else 0,
                    "rr": float(str(row[col_rr]).replace(",", ".") or 0) if col_rr != "—" else 0,
                    "setup": "Import Manuel",
                    "notes": "",
                    "session": "London",
                    "result": "",
                }
                t["result"] = "Win" if t["pnl"] > 0 else "Loss"
                new_trades.append(t)
            st.session_state.trades.extend(new_trades)
            st.success(f"✅ {len(new_trades)} trades importés !")
            st.rerun()


def page_data():
    st.markdown('<div class="page-title">Gestion des Données</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Sauvegarde, restaure ou réinitialise tes données</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 💾 Exporter")
        if st.session_state.trades:
            # JSON
            json_data = save_trades_json()
            st.download_button(
                "⬇️ Télécharger JSON",
                data=json_data,
                file_name=f"mvizion_trades_{date.today()}.json",
                mime="application/json",
                use_container_width=True
            )
            # CSV
            df = trades_df()
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Télécharger CSV",
                data=csv_data,
                file_name=f"mvizion_trades_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Aucune donnée à exporter.")

    with c2:
        st.markdown("### 📤 Importer")
        uploaded = st.file_uploader("Charger un fichier JSON mVizion", type=["json"])
        if uploaded:
            if st.button("✅ Restaurer les données"):
                try:
                    load_trades_json(uploaded.read())
                    st.success("Données restaurées !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

    st.markdown("---")
    st.markdown("### 🗑️ Réinitialisation")
    with st.expander("Zone de danger ⚠️"):
        st.warning("Cette action supprimera TOUS tes trades de façon définitive.")
        confirm = st.text_input("Tape RESET pour confirmer")
        if st.button("Réinitialiser tout") and confirm == "RESET":
            st.session_state.trades = []
            st.success("Données effacées.")
            st.rerun()

    # Stats
    if st.session_state.trades:
        st.markdown("---")
        df = trades_df()
        st.markdown(f"""
        <div class="card">
            <div class="kpi-label">Statistiques de stockage</div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:.8rem;">
                <div>
                    <div style="font-size:.72rem;color:#6b7280;margin-bottom:.2rem;">Trades</div>
                    <div style="font-size:1.3rem;font-weight:700;font-family:'Syne',sans-serif;color:#7c6fff;">{len(df)}</div>
                </div>
                <div>
                    <div style="font-size:.72rem;color:#6b7280;margin-bottom:.2rem;">Symboles</div>
                    <div style="font-size:1.3rem;font-weight:700;font-family:'Syne',sans-serif;color:#4fffb0;">{df['symbol'].nunique()}</div>
                </div>
                <div>
                    <div style="font-size:.72rem;color:#6b7280;margin-bottom:.2rem;">Période</div>
                    <div style="font-size:.9rem;font-weight:600;color:#ffd166;">{str(df['date'].min())[:10]} → {str(df['date'].max())[:10]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    init_state()
    sidebar()

    page = st.session_state.page
    if page == "Dashboard":
        page_dashboard()
    elif page == "Journal":
        page_journal()
    elif page == "Ajouter Trade":
        page_add_trade()
    elif page == "Import CSV":
        page_import()
    elif page == "Données":
        page_data()

if __name__ == "__main__":
    main()
