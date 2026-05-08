import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from datetime import datetime, date
import io

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
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
.main { background: var(--bg) !important; }
.block-container { padding: 1.5rem 2rem !important; }

.card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
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
.kpi-value { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; line-height: 1; }
.kpi-sub { font-size: 0.75rem; color: var(--muted); margin-top: .3rem; }
.green { color: var(--accent1) !important; }
.red   { color: var(--accent3) !important; }
.gold  { color: var(--accent4) !important; }
.purple{ color: var(--accent2) !important; }

.trade-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.trade-table th {
    font-family: 'DM Mono', monospace; font-size: 0.68rem;
    text-transform: uppercase; letter-spacing: .08em;
    color: var(--muted); padding: .7rem 1rem;
    border-bottom: 1px solid var(--border); text-align: left;
}
.trade-table td { padding: .65rem 1rem; border-bottom: 1px solid #1a1f2a; color: var(--text); }
.trade-table tr:hover td { background: var(--bg3); }

.badge { display: inline-block; padding: .2rem .6rem; border-radius: 6px; font-size: 0.72rem; font-weight: 600; font-family: 'DM Mono', monospace; }
.badge-long  { background: rgba(78,255,176,.15); color: var(--accent1); }
.badge-short { background: rgba(255,107,107,.15); color: var(--accent3); }
.badge-win   { background: rgba(78,255,176,.12); color: var(--accent1); }
.badge-loss  { background: rgba(255,107,107,.12); color: var(--accent3); }

.stButton button {
    background: linear-gradient(135deg, var(--accent1), var(--accent2)) !important;
    color: #0a0c10 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
}
.page-title {
    font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800;
    background: linear-gradient(90deg, var(--accent1), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.page-subtitle { font-size: .85rem; color: var(--muted); margin-bottom: 1.5rem; }
.logo {
    font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800;
    background: linear-gradient(90deg, var(--accent1), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─── State ───────────────────────────────────────────────────────────────────
if "trades" not in st.session_state:
    st.session_state.trades = []

# ─── Helpers ─────────────────────────────────────────────────────────────────
def trades_df():
    if not st.session_state.trades:
        return pd.DataFrame()
    df = pd.DataFrame(st.session_state.trades)
    df["date"] = pd.to_datetime(df["date"])
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
    df["rr"] = pd.to_numeric(df["rr"], errors="coerce")
    df.sort_values("date", ascending=False, inplace=True)
    return df

def compute_kpis(df):
    if df.empty:
        return {"total_pnl": 0, "win_rate": 0, "total_trades": 0, "avg_rr": 0,
                "best_trade": 0, "worst_trade": 0, "profit_factor": 0, "streak": 0}
    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] <= 0]
    total_pnl = df["pnl"].sum()
    win_rate = len(wins) / len(df) * 100
    avg_rr = df["rr"].mean()
    gross_profit = wins["pnl"].sum() if not wins.empty else 0
    gross_loss = abs(losses["pnl"].sum()) if not losses.empty else 1
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
    results = df.sort_values("date")["pnl"].tolist()
    streak = 0
    for p in reversed(results):
        if (p > 0 and streak >= 0) or (p <= 0 and streak <= 0):
            streak += 1 if p > 0 else -1
        else:
            break
    return {"total_pnl": total_pnl, "win_rate": win_rate, "total_trades": len(df),
            "avg_rr": avg_rr if not np.isnan(avg_rr) else 0,
            "best_trade": df["pnl"].max(), "worst_trade": df["pnl"].min(),
            "profit_factor": profit_factor, "streak": streak}

CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e8eaf0", font_family="Plus Jakarta Sans",
    xaxis=dict(gridcolor="#1e2330", zerolinecolor="#1e2330"),
    yaxis=dict(gridcolor="#1e2330", zerolinecolor="#1e2330"),
    margin=dict(l=10, r=10, t=30, b=10),
)

def parse_tradingview_csv(df_raw):
    col_map = {"Trade #": "id","Symbol": "symbol","Type": "direction",
               "Entry": "entry","Exit": "exit","Profit": "pnl","Date/Time": "date","Qty": "qty"}
    mapped = {}
    for src, dst in col_map.items():
        for c in df_raw.columns:
            if src.lower() in c.lower():
                mapped[dst] = c
                break
    trades_out = []
    for _, row in df_raw.iterrows():
        pnl_raw = str(row.get(mapped.get("pnl", ""), 0)).replace(",", "").replace(" ", "").replace("%","")
        try: pnl_val = float(pnl_raw)
        except: pnl_val = 0.0
        t = {
            "id": str(len(st.session_state.trades) + len(trades_out) + 1),
            "symbol": str(row.get(mapped.get("symbol", ""), "UNKNOWN")),
            "direction": "Long" if "long" in str(row.get(mapped.get("direction", ""), "")).lower() else "Short",
            "entry": float(str(row.get(mapped.get("entry", ""), 0)).replace(",", ".") or 0),
            "exit": float(str(row.get(mapped.get("exit", ""), 0)).replace(",", ".") or 0),
            "qty": float(str(row.get(mapped.get("qty", ""), 1)).replace(",", ".") or 1),
            "pnl": pnl_val,
            "date": str(row.get(mapped.get("date", ""), str(date.today()))),
            "rr": 0.0, "setup": "Import TV", "notes": "", "session": "London",
        }
        t["result"] = "Win" if t["pnl"] > 0 else "Loss"
        trades_out.append(t)
    return trades_out


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo">m<span style="color:#e8eaf0">Vizion</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.72rem;color:#6b7280;margin-bottom:1.5rem;font-family:\'DM Mono\',monospace;">TRADING JOURNAL · INDICES</div>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📋 Journal", "➕ Ajouter Trade", "📥 Import CSV", "💾 Données"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    df_side = trades_df()
    if not df_side.empty:
        kpis_side = compute_kpis(df_side)
        color_s = "#4fffb0" if kpis_side["total_pnl"] >= 0 else "#ff6b6b"
        sign_s = "+" if kpis_side["total_pnl"] >= 0 else ""
        st.markdown(f"""
        <div style="background:#181c24;border-radius:12px;padding:1rem;border:1px solid #232836">
            <div style="font-size:.68rem;color:#6b7280;font-family:'DM Mono',monospace;text-transform:uppercase;margin-bottom:.5rem;">RÉSUMÉ</div>
            <div style="color:{color_s};font-size:1.3rem;font-family:'Syne',sans-serif;font-weight:800;">{sign_s}{kpis_side['total_pnl']:,.2f}€</div>
            <div style="font-size:.75rem;color:#6b7280;margin-top:.3rem;">{kpis_side['total_trades']} trades · {kpis_side['win_rate']:.0f}% WR</div>
        </div>
        """, unsafe_allow_html=True)


# ─── Dashboard ───────────────────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Vue d\'ensemble de tes performances de trading</div>', unsafe_allow_html=True)

    df = trades_df()
    if df.empty:
        st.info("💡 Aucun trade enregistré. Commence par **➕ Ajouter Trade** ou **📥 Import CSV**.")
    else:
        kpis = compute_kpis(df)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            sign = "+" if kpis["total_pnl"] >= 0 else ""
            color = "green" if kpis["total_pnl"] >= 0 else "red"
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">P&L Total</div><div class="kpi-value {color}">{sign}{kpis["total_pnl"]:,.2f}€</div><div class="kpi-sub">{kpis["total_trades"]} trades</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Win Rate</div><div class="kpi-value purple">{kpis["win_rate"]:.1f}%</div><div class="kpi-sub">objectif ≥ 55%</div></div>', unsafe_allow_html=True)
        with c3:
            pfc = "green" if kpis["profit_factor"] >= 1 else "red"
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Profit Factor</div><div class="kpi-value {pfc}">{kpis["profit_factor"]:.2f}</div><div class="kpi-sub">objectif ≥ 1.5</div></div>', unsafe_allow_html=True)
        with c4:
            sc = "green" if kpis["streak"] > 0 else "red"
            sl = f'+{kpis["streak"]} wins' if kpis["streak"] > 0 else f'{kpis["streak"]} losses'
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Série en cours</div><div class="kpi-value {sc}">{sl}</div><div class="kpi-sub">Avg R:R {kpis["avg_rr"]:.2f}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Equity curve
        df2 = df.sort_values("date").copy()
        df2["cumulative"] = df2["pnl"].cumsum()
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(x=df2["date"], y=df2["cumulative"], mode="lines",
            line=dict(color="#4fffb0", width=2.5), fill="tozeroy", fillcolor="rgba(78,255,176,0.07)"))
        fig_eq.update_layout(**CHART_THEME, height=280, title="Courbe d'équité")

        col1, col2 = st.columns([2.5, 1])
        with col1:
            st.plotly_chart(fig_eq, use_container_width=True, config={"displayModeBar": False})
        with col2:
            fig_d = go.Figure(go.Pie(
                values=[kpis["win_rate"], 100 - kpis["win_rate"]], labels=["Wins", "Losses"],
                hole=0.72, marker_colors=["#4fffb0", "#ff6b6b"], textinfo="none"))
            fig_d.update_layout(**CHART_THEME, height=240, showlegend=False,
                annotations=[dict(text=f'{kpis["win_rate"]:.0f}%', x=0.5, y=0.5,
                    font=dict(size=26, color="#e8eaf0", family="Syne"), showarrow=False)])
            st.markdown('<div style="text-align:center;font-size:.75rem;color:#6b7280;font-family:\'DM Mono\',monospace;text-transform:uppercase;padding-top:.5rem;">Win Rate</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})

        col3, col4 = st.columns(2)
        with col3:
            colors_bar = ["#4fffb0" if p > 0 else "#ff6b6b" for p in df2["pnl"]]
            fig_bar = go.Figure(go.Bar(x=df2["date"], y=df2["pnl"], marker_color=colors_bar))
            fig_bar.update_layout(**CHART_THEME, height=240, title="P&L par trade")
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        with col4:
            df2["month"] = df2["date"].dt.to_period("M").astype(str)
            monthly = df2.groupby("month")["pnl"].sum().reset_index()
            colors_m = ["#4fffb0" if p > 0 else "#ff6b6b" for p in monthly["pnl"]]
            fig_m = go.Figure(go.Bar(x=monthly["month"], y=monthly["pnl"], marker_color=colors_m))
            fig_m.update_layout(**CHART_THEME, height=240, title="P&L Mensuel")
            st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})

        col5, col6 = st.columns(2)
        with col5:
            sym = df.groupby("symbol")["pnl"].sum().sort_values().reset_index()
            colors_s = ["#4fffb0" if p > 0 else "#ff6b6b" for p in sym["pnl"]]
            fig_s = go.Figure(go.Bar(x=sym["pnl"], y=sym["symbol"], orientation="h", marker_color=colors_s))
            fig_s.update_layout(**CHART_THEME, height=260, title="Performance par symbole")
            st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})
        with col6:
            best = df.loc[df["pnl"].idxmax()]
            worst = df.loc[df["pnl"].idxmin()]
            st.markdown(f"""
            <div class="card">
                <div class="kpi-label">🏆 Meilleur Trade</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#4fffb0;">+{best['pnl']:,.2f}€</div>
                <div style="color:#6b7280;font-size:.8rem;margin-top:.3rem;">{best['symbol']} · {str(best['date'])[:10]}</div>
            </div>
            <div class="card">
                <div class="kpi-label">📉 Pire Trade</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#ff6b6b;">{worst['pnl']:,.2f}€</div>
                <div style="color:#6b7280;font-size:.8rem;margin-top:.3rem;">{worst['symbol']} · {str(worst['date'])[:10]}</div>
            </div>
            """, unsafe_allow_html=True)


# ─── Journal ─────────────────────────────────────────────────────────────────
elif page == "📋 Journal":
    st.markdown('<div class="page-title">Journal des Trades</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Historique complet de tes positions</div>', unsafe_allow_html=True)

    df = trades_df()
    if df.empty:
        st.info("Aucun trade pour l'instant.")
    else:
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            sym_filter = st.selectbox("Symbole", ["Tous"] + sorted(df["symbol"].unique().tolist()))
        with fc2:
            dir_filter = st.selectbox("Direction", ["Tous", "Long", "Short"])
        with fc3:
            res_filter = st.selectbox("Résultat", ["Tous", "Win", "Loss"])

        df_f = df.copy()
        if sym_filter != "Tous": df_f = df_f[df_f["symbol"] == sym_filter]
        if dir_filter != "Tous": df_f = df_f[df_f["direction"] == dir_filter]
        if res_filter != "Tous": df_f = df_f[df_f["result"] == res_filter]

        st.markdown(f'<div style="color:#6b7280;font-size:.8rem;margin:.5rem 0;">{len(df_f)} trade(s)</div>', unsafe_allow_html=True)

        rows = ""
        for _, t in df_f.iterrows():
            pnl_color = "#4fffb0" if float(t["pnl"]) > 0 else "#ff6b6b"
            sign = "+" if float(t["pnl"]) > 0 else ""
            dir_b = f'<span class="badge badge-long">Long</span>' if t["direction"] == "Long" else f'<span class="badge badge-short">Short</span>'
            res_b = f'<span class="badge badge-win">Win</span>' if t.get("result") == "Win" else f'<span class="badge badge-loss">Loss</span>'
            rows += f"""<tr>
                <td style="font-family:'DM Mono',monospace;font-size:.78rem;">{str(t['date'])[:10]}</td>
                <td style="font-weight:600;">{t['symbol']}</td>
                <td>{dir_b}</td>
                <td style="font-family:'DM Mono',monospace;">{float(t['entry']):.2f}</td>
                <td style="font-family:'DM Mono',monospace;">{float(t['exit']):.2f}</td>
                <td style="font-family:'DM Mono',monospace;color:{pnl_color};font-weight:600;">{sign}{float(t['pnl']):.2f}€</td>
                <td style="font-family:'DM Mono',monospace;">{float(t.get('rr',0)):.2f}</td>
                <td style="font-size:.78rem;color:#7c6fff;">{t.get('setup','')}</td>
                <td>{res_b}</td>
            </tr>"""

        st.markdown(f"""<table class="trade-table"><thead><tr>
            <th>Date</th><th>Symbole</th><th>Direction</th>
            <th>Entrée</th><th>Sortie</th><th>P&L</th><th>R:R</th><th>Setup</th><th>Résultat</th>
        </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🗑️ Supprimer un trade"):
            ids = [f"#{t['id']} · {t['symbol']} · {str(t['date'])[:10]}" for t in st.session_state.trades]
            if ids:
                to_del = st.selectbox("Trade à supprimer", ids)
                if st.button("Supprimer"):
                    st.session_state.trades.pop(ids.index(to_del))
                    st.success("Trade supprimé !")
                    st.rerun()


# ─── Ajouter Trade ───────────────────────────────────────────────────────────
elif page == "➕ Ajouter Trade":
    st.markdown('<div class="page-title">Ajouter un Trade</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enregistre manuellement une nouvelle position</div>', unsafe_allow_html=True)

    with st.form("add_trade_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            symbol = st.text_input("Symbole *", placeholder="CAC40, SP500, NQ...")
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
                st.session_state.trades.append({
                    "id": str(len(st.session_state.trades) + 1),
                    "symbol": symbol.upper(), "direction": direction,
                    "date": str(trade_date), "entry": float(entry),
                    "exit": float(exit_p), "qty": float(qty),
                    "pnl": float(pnl), "rr": float(rr),
                    "setup": setup, "result": result,
                    "session": session, "notes": notes,
                })
                st.success(f"✅ Trade {symbol.upper()} enregistré !")
                st.balloons()


# ─── Import CSV ──────────────────────────────────────────────────────────────
elif page == "📥 Import CSV":
    st.markdown('<div class="page-title">Import CSV TradingView</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Importe tes trades depuis TradingView ou tout autre fichier CSV</div>', unsafe_allow_html=True)

    with st.expander("📖 Comment exporter depuis TradingView ?"):
        st.markdown("""
        1. Ouvre ton **Strategy Tester** sur TradingView
        2. Clique sur **"Liste des trades"**
        3. Clique sur **"Exporter les données"** (icône ↓)
        4. Importe le CSV ici !

        **Colonnes reconnues automatiquement :** Trade #, Symbol, Type, Entry, Exit, Profit, Date/Time, Qty
        """)

    tab1, tab2 = st.tabs(["📂 Import Fichier", "🔧 Mapping Manuel"])

    with tab1:
        uploaded = st.file_uploader("Dépose ton fichier CSV ici", type=["csv"])
        sep = st.selectbox("Séparateur", [",", ";", "\t"])

        if uploaded:
            try:
                df_raw = pd.read_csv(uploaded, sep=sep)
                st.success(f"✅ {len(df_raw)} lignes détectées")
                st.dataframe(df_raw.head(5), use_container_width=True)
                if st.button("🚀 Importer (auto-mapping TradingView)", use_container_width=True):
                    new_trades = parse_tradingview_csv(df_raw)
                    st.session_state.trades.extend(new_trades)
                    st.success(f"✅ {len(new_trades)} trades importés !")
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

    with tab2:
        uploaded2 = st.file_uploader("Fichier CSV", type=["csv"], key="manual")
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
                    try: pnl_v = float(str(row[col_pnl]).replace(",","").replace(" ","")) if col_pnl != "—" else 0
                    except: pnl_v = 0
                    t = {
                        "id": str(len(st.session_state.trades) + len(new_trades) + 1),
                        "symbol": str(row[col_sym]) if col_sym != "—" else "UNKNOWN",
                        "direction": str(row[col_dir]) if col_dir != "—" else "Long",
                        "date": str(row[col_date]) if col_date != "—" else str(date.today()),
                        "entry": float(str(row[col_entry]).replace(",",".") or 0) if col_entry != "—" else 0,
                        "exit": float(str(row[col_exit]).replace(",",".") or 0) if col_exit != "—" else 0,
                        "qty": float(str(row[col_qty]).replace(",",".") or 1) if col_qty != "—" else 1,
                        "pnl": pnl_v,
                        "rr": float(str(row[col_rr]).replace(",",".") or 0) if col_rr != "—" else 0,
                        "setup": "Import Manuel", "notes": "", "session": "London",
                    }
                    t["result"] = "Win" if t["pnl"] > 0 else "Loss"
                    new_trades.append(t)
                st.session_state.trades.extend(new_trades)
                st.success(f"✅ {len(new_trades)} trades importés !")
                st.rerun()


# ─── Données ─────────────────────────────────────────────────────────────────
elif page == "💾 Données":
    st.markdown('<div class="page-title">Gestion des Données</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Sauvegarde, restaure ou réinitialise tes données</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 💾 Exporter")
        if st.session_state.trades:
            json_data = json.dumps(st.session_state.trades, default=str, indent=2)
            st.download_button("⬇️ Télécharger JSON", data=json_data,
                file_name=f"mvizion_{date.today()}.json", mime="application/json", use_container_width=True)
            df = trades_df()
            st.download_button("⬇️ Télécharger CSV", data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"mvizion_{date.today()}.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("Aucune donnée à exporter.")

    with c2:
        st.markdown("### 📤 Importer sauvegarde")
        uploaded_j = st.file_uploader("Charger JSON mVizion", type=["json"])
        if uploaded_j:
            if st.button("✅ Restaurer"):
                try:
                    st.session_state.trades = json.loads(uploaded_j.read())
                    st.success("Données restaurées !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

    st.markdown("---")
    with st.expander("⚠️ Zone de danger — Réinitialisation"):
        st.warning("Cette action supprimera TOUS tes trades.")
        confirm = st.text_input("Tape RESET pour confirmer")
        if st.button("Réinitialiser tout") and confirm == "RESET":
            st.session_state.trades = []
            st.success("Données effacées.")
            st.rerun()
