import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import pytz
from ai_agent import answer_question, get_stock_data, get_world_news
from collector import run_collection
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="StockWatch AI", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# ── SESSION STATE ──
defaults = [("ai_question",""),("ai_answer",""),("chart_symbol","AAPL"),("selected_index",None),("watchlist",["AAPL","TSLA","NVDA","MSFT","AMZN"]),("chart_period","1mo"),("pending_question","")]
for key, val in defaults:
    if key not in st.session_state:
        st.session_state[key] = val

# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif;background-color:#080c14;color:#e2e8f0;}
.stApp{background:linear-gradient(135deg,#080c14 0%,#0d1520 50%,#080c14 100%);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1rem;padding-bottom:2rem;}
/* SIDEBAR - always open, no collapse */
section[data-testid="stSidebar"]{background:#060e1a !important;border-right:1px solid #1e3a5f !important;}
section[data-testid="stSidebar"] > div{min-width:260px !important;}
[data-testid="collapsedControl"]{display:none !important;visibility:hidden !important;pointer-events:none !important;}
[data-testid="stSidebarCollapseButton"]{display:none !important;visibility:hidden !important;pointer-events:none !important;}
button[data-testid="baseButton-header"]{display:none !important;}
/* HEADER */
.sw-header{background:linear-gradient(90deg,#0d1520,#0a1628);border-bottom:1px solid #1e3a5f;padding:1rem 2rem;margin:-1rem -1rem 1.5rem -1rem;display:flex;align-items:center;justify-content:space-between;}
.sw-logo{font-family:'Space Mono',monospace;font-size:1.5rem;font-weight:700;color:#38bdf8;letter-spacing:-1px;}
.sw-logo span{color:#f59e0b;}
.sw-tagline{font-size:0.65rem;color:#64748b;letter-spacing:2px;text-transform:uppercase;margin-top:2px;}
.sw-time{font-family:'Space Mono',monospace;font-size:0.8rem;color:#38bdf8;text-align:right;}
/* CARDS */
.metric-card{background:linear-gradient(135deg,#0d1929 0%,#111f33 100%);border:1px solid #1e3a5f;border-radius:12px;padding:1rem 1.2rem;position:relative;overflow:hidden;transition:all 0.2s;}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#38bdf8,#6366f1);}
.metric-card:hover{border-color:#38bdf8;transform:translateY(-2px);}
.metric-label{font-size:0.65rem;color:#64748b;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.3rem;font-family:'Space Mono',monospace;}
.metric-value{font-size:1.5rem;font-weight:800;color:#f1f5f9;font-family:'Space Mono',monospace;line-height:1;}
.metric-change{font-size:0.8rem;font-family:'Space Mono',monospace;margin-top:0.3rem;}
.up{color:#22c55e !important;}.down{color:#ef4444 !important;}.neutral{color:#94a3b8 !important;}
.section-header{font-size:0.65rem;letter-spacing:3px;text-transform:uppercase;color:#38bdf8;font-family:'Space Mono',monospace;border-left:3px solid #38bdf8;padding-left:0.75rem;margin-bottom:0.8rem;}
/* AI */
.ai-answer{background:#060e1a;border:1px solid #1e3a5f;border-left:3px solid #38bdf8;border-radius:8px;padding:1.2rem;margin-top:0.8rem;font-size:0.9rem;line-height:1.7;color:#cbd5e1;}
/* NEWS */
.news-desc{font-size:0.78rem;color:#94a3b8;line-height:1.5;margin-top:0.4rem;}
.news-category{display:inline-block;background:#1e3a5f;color:#38bdf8;font-size:0.58rem;padding:2px 7px;border-radius:20px;text-transform:uppercase;letter-spacing:1px;margin-right:0.4rem;}
.ticker-badge{display:inline-block;background:#1e3a5f;color:#38bdf8;font-family:'Space Mono',monospace;font-size:0.72rem;font-weight:700;padding:2px 8px;border-radius:4px;margin-right:0.4rem;}
/* SUPPORT */
.support-level{background:#0d1929;border:1px solid #1e3a5f;border-radius:8px;padding:0.7rem 0.9rem;margin-bottom:0.4rem;}
.support-label{font-size:0.6rem;color:#64748b;font-family:'Space Mono',monospace;text-transform:uppercase;letter-spacing:1px;}
.support-value{font-size:0.95rem;font-weight:700;font-family:'Space Mono',monospace;}
.inst-card{background:#0d1929;border:1px solid #1e3a5f;border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.5rem;}
/* FEAR GAUGE */
.fear-gauge{background:#0d1929;border:1px solid #1e3a5f;border-radius:12px;padding:1.2rem;text-align:center;min-height:130px;}
/* SIDEBAR BUTTONS */
section[data-testid="stSidebar"] .stButton button{background:#0d1929;color:#94a3b8;border:1px solid #1e3a5f;border-radius:6px;font-size:0.75rem;width:100%;text-align:left;padding:0.35rem 0.7rem;transition:all 0.2s;}
section[data-testid="stSidebar"] .stButton button:hover{background:#1e3a5f;color:#38bdf8;border-color:#38bdf8;}
/* INPUTS */
.stTextInput input{background:#060e1a !important;border:1px solid #1e3a5f !important;color:#e2e8f0 !important;border-radius:8px !important;}
.stTextInput input:focus{border-color:#38bdf8 !important;box-shadow:0 0 0 2px rgba(56,189,248,0.15) !important;}
/* SELECT */
.stSelectbox [data-baseweb="select"]{background:#060e1a !important;border-color:#1e3a5f !important;}
/* MISC */
hr{border-color:#1e3a5f !important;margin:1rem 0 !important;}
.live-dot{display:inline-block;width:7px;height:7px;background:#22c55e;border-radius:50%;margin-right:5px;animation:pulse 2s infinite;}
.live-dot.red{background:#ef4444;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(0.8)}}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#060e1a;}
::-webkit-scrollbar-thumb{background:#1e3a5f;border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:#38bdf8;}
.stTabs [data-baseweb="tab-list"]{background:#0a1221;border-radius:8px;padding:4px;}
.stTabs [data-baseweb="tab"]{color:#64748b;font-family:'Space Mono',monospace;font-size:0.72rem;}
.stTabs [aria-selected="true"]{color:#38bdf8 !important;}
</style>
""", unsafe_allow_html=True)

# Force sidebar always expanded via JS
import streamlit.components.v1 as components
components.html("""
<script>
(function() {
    function forceSidebar() {
        try {
            var doc = window.parent.document;
            // Keep sidebar open
            var sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                if (sidebar.getAttribute('aria-expanded') === 'false') {
                    sidebar.setAttribute('aria-expanded', 'true');
                }
                sidebar.style.setProperty('transform', 'none', 'important');
                sidebar.style.setProperty('margin-left', '0px', 'important');
                sidebar.style.setProperty('visibility', 'visible', 'important');
            }
            // Hide ALL collapse/expand buttons
            var btns = doc.querySelectorAll('[data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"]');
            btns.forEach(function(btn) {
                btn.style.setProperty('display', 'none', 'important');
                btn.style.setProperty('visibility', 'hidden', 'important');
            });
        } catch(e) {}
    }
    forceSidebar();
    setInterval(forceSidebar, 500);
})();
</script>
""", height=0)


# ── PERIOD MAP ──
PERIOD_OPTIONS = ["1min","2min","5min","15min","30min","1hr","4hr","1day","1week","1mo","3mo","6mo","1yr"]
PERIOD_MAP = {
    "1min":  ("1d",   "1m"),
    "2min":  ("1d",   "2m"),
    "5min":  ("5d",   "5m"),
    "15min": ("5d",   "15m"),
    "30min": ("5d",   "30m"),
    "1hr":   ("1mo",  "1h"),
    "4hr":   ("3mo",  "1h"),
    "1day":  ("1y",   "1d"),
    "1week": ("1y",   "1wk"),
    "1mo":   ("6mo",  "1d"),
    "3mo":   ("3mo",  "1d"),
    "6mo":   ("6mo",  "1d"),
    "1yr":   ("1y",   "1d"),
}

# ── CACHED FUNCTIONS ──
@st.cache_data(ttl=120)
def get_index_data():
    indices = {"S&P 500":"^GSPC","NASDAQ":"^IXIC","DOW JONES":"^DJI","VIX":"^VIX"}
    results = {}
    for name, symbol in indices.items():
        try:
            info = yf.Ticker(symbol).info
            price = info.get("regularMarketPrice") or info.get("previousClose",0)
            prev = info.get("regularMarketPreviousClose",0)
            change = ((price-prev)/prev*100) if prev and prev != price else 0
            results[name] = {"price":price,"change":change,"symbol":symbol}
        except:
            results[name] = {"price":0,"change":0,"symbol":symbol}
    return results

@st.cache_data(ttl=300)
def get_chart_data(symbol, period):
    try:
        yf_period, yf_interval = PERIOD_MAP.get(period, ("2y","1mo"))
        return yf.Ticker(symbol).history(period=yf_period, interval=yf_interval)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_live_price(symbol):
    try:
        info = yf.Ticker(symbol).info
        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose",0)
        prev = info.get("regularMarketPreviousClose",price)
        change = ((price-prev)/prev*100) if prev else 0
        return {
            "price":price,"change":change,"company":info.get("shortName",symbol),
            "high":info.get("dayHigh",0),"low":info.get("dayLow",0),
            "volume":info.get("regularMarketVolume",0),"market_cap":info.get("marketCap",0),
            "pre_market":info.get("preMarketPrice",0),"post_market":info.get("postMarketPrice",0),
        }
    except:
        return {"price":0,"change":0,"company":symbol}

@st.cache_data(ttl=300)
def get_support_resistance(symbol):
    try:
        hist = yf.Ticker(symbol).history(period="6mo")
        if hist.empty: return None
        current = hist['Close'].iloc[-1]
        r20 = hist.tail(20); r60 = hist.tail(60)
        resistance1 = round(r20['High'].max(),2)
        resistance2 = round(r60['High'].quantile(0.9),2)
        support1 = round(r20['Low'].min(),2)
        support2 = round(r60['Low'].quantile(0.1),2)
        ma20 = round(hist['Close'].rolling(20).mean().iloc[-1],2)
        ma50 = round(hist['Close'].rolling(50).mean().iloc[-1],2) if len(hist)>=50 else ma20
        ma200 = round(hist['Close'].rolling(200).mean().iloc[-1],2) if len(hist)>=200 else ma50
        bb_mid = hist['Close'].rolling(20).mean().iloc[-1]
        bb_std = hist['Close'].rolling(20).std().iloc[-1]
        bb_upper = round(bb_mid + 2*bb_std,2)
        bb_lower = round(bb_mid - 2*bb_std,2)
        daily_vol = hist['Close'].pct_change().std()
        weekly_vol = daily_vol * (5**0.5)
        return {
            "current":current,"resistance2":resistance2,"resistance1":resistance1,
            "ma20":ma20,"ma50":ma50,"ma200":ma200,"support1":support1,"support2":support2,
            "high_52w":round(hist['High'].max(),2),"low_52w":round(hist['Low'].min(),2),
            "bb_upper":bb_upper,"bb_lower":bb_lower,
            "expected_up":round(current*(1+weekly_vol),2),"expected_down":round(current*(1-weekly_vol),2),
            "breakout_level":resistance1,"breakdown_level":support1,
        }
    except:
        return None

@st.cache_data(ttl=3600)
def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=5)
        data = r.json()
        return {"value":int(data['data'][0]['value']),"label":data['data'][0]['value_classification']}
    except:
        return {"value":50,"label":"Neutral"}

@st.cache_data(ttl=300)
def get_most_active():
    symbols = ["NVDA","TSLA","AAPL","AMD","AMZN","META","MSFT","PLTR","SPY","QQQ"]
    results = []
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            fi = t.fast_info
            price = fi.last_price or 0
            prev = fi.previous_close or price
            change = ((price-prev)/prev*100) if prev else 0
            vol = fi.three_month_average_volume or 0
            results.append({"symbol":sym,"price":price,"change":change,"volume":vol})
        except:
            pass
    return sorted(results, key=lambda x: x.get("volume",0), reverse=True)

@st.cache_data(ttl=300)
def get_crypto_prices():
    results = []
    for symbol, name in {"BTC-USD":"Bitcoin","ETH-USD":"Ethereum","SOL-USD":"Solana"}.items():
        try:
            fi = yf.Ticker(symbol).fast_info
            price = fi.last_price or 0
            prev = fi.previous_close or price
            change = ((price-prev)/prev*100) if prev else 0
            results.append({"symbol":symbol.replace("-USD",""),"name":name,"price":price,"change":change})
        except:
            pass
    return results

def get_sector_data():
    # Uses database prices - fast, no extra API calls
    sectors = {
        "Technology":["AAPL","MSFT","NVDA","AMD","INTC"],
        "Consumer":["AMZN","WMT","MCD","KO","PEP"],
        "Finance":["JPM","GS","MS","BAC","BLK"],
        "Healthcare":["JNJ","UNH","MRK","ABBV","AMGN"],
        "Energy":["XOM","CVX","COP","SLB","EOG"],
        "Defense":["RTX","LMT","NOC","GD","BA"],
    }
    try:
        import sqlite3
        import pandas as pd
        conn = sqlite3.connect("stockwatch.db")
        prices_df = pd.read_sql("SELECT symbol, change_percent FROM stock_prices ORDER BY date DESC", conn)
        conn.close()
        results = []
        for sector, syms in sectors.items():
            sector_stocks = prices_df[prices_df['symbol'].isin(syms)]
            if not sector_stocks.empty:
                avg = round(sector_stocks['change_percent'].mean(), 2)
                results.append({"Sector":sector,"Avg Change":avg})
        return results
    except:
        return []

def get_top_losers():
    # Uses database prices - fast
    try:
        import sqlite3
        import pandas as pd
        conn = sqlite3.connect("stockwatch.db")
        df = pd.read_sql("SELECT symbol, company, price, change_percent FROM stock_prices ORDER BY date DESC", conn)
        conn.close()
        losers = df[df['change_percent'] < 0].sort_values('change_percent').head(10)
        return [{"symbol":r['symbol'],"price":r['price'],"change":r['change_percent']} for _,r in losers.iterrows()]
    except:
        return []


# ── HEADER ──
est = pytz.timezone('US/Eastern')
now_est = datetime.now(est)
now_local = datetime.now()
is_weekday = now_est.weekday() < 5
is_open = is_weekday and now_est.replace(hour=9,minute=30,second=0) <= now_est <= now_est.replace(hour=16,minute=0,second=0)
market_status = "MARKET OPEN" if is_open else "MARKET CLOSED"
status_color = "#22c55e" if is_open else "#ef4444"
dot_class = "live-dot" if is_open else "live-dot red"

st.markdown(f"""
<div class="sw-header">
    <div><div class="sw-logo">Stock<span>Watch</span> AI</div><div class="sw-tagline">Real-Time US Market Intelligence · RAG Powered</div></div>
    <div style="text-align:center;"><span class="{dot_class}"></span><span style="color:{status_color};font-family:'Space Mono',monospace;font-size:0.85rem;font-weight:700;">{market_status}</span><br><span style="font-size:0.65rem;color:#475569;font-family:'Space Mono',monospace;">EST {now_est.strftime("%H:%M:%S")}</span></div>
    <div class="sw-time">{now_local.strftime("%A, %B %d %Y")}<br><span style="font-size:1.1rem;">{now_local.strftime("%H:%M:%S")}</span></div>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<div class="section-header">CONTROLS</div>', unsafe_allow_html=True)
    if st.button("🔄 Refresh Market Data", use_container_width=True):
        with st.spinner("Collecting latest data..."):
            run_collection()
            st.cache_data.clear()
        st.success("✓ Data refreshed!")

    st.markdown("---")
    st.markdown('<div class="section-header">⭐ WATCHLIST</div>', unsafe_allow_html=True)
    for sym in st.session_state.watchlist:
        d = get_live_price(sym)
        if d["price"] > 0:
            chg_color = "#22c55e" if d["change"]>=0 else "#ef4444"
            arrow = "▲" if d["change"]>=0 else "▼"
            c1,c2 = st.columns([3,2])
            with c1:
                if st.button(f"{sym} ${d['price']:.2f}", key=f"wl_{sym}", use_container_width=True):
                    st.session_state.chart_symbol = sym
                    st.session_state.ai_question = f"Tell me about {sym} today"
                    st.session_state.ai_answer = ""
                    st.rerun()
            with c2:
                st.markdown(f'<div style="color:{chg_color};font-family:Space Mono,monospace;font-size:0.7rem;padding-top:6px;">{arrow}{abs(d["change"]):.1f}%</div>', unsafe_allow_html=True)

    wl_input = st.text_input("Add symbol:", placeholder="SYMBOL", key="add_watch")
    if st.button("+ Add to Watchlist", use_container_width=True):
        if wl_input and wl_input.strip():
            sym = wl_input.upper().strip()
            if sym not in st.session_state.watchlist:
                st.session_state.watchlist.append(sym)
                st.success(f"✓ {sym} added!")
            else:
                st.info(f"{sym} already in watchlist")
            st.rerun()
        else:
            st.warning("Enter a symbol first")

    st.markdown("---")
    st.markdown('<div class="section-header">QUICK SEARCH</div>', unsafe_allow_html=True)
    quick_symbol = st.text_input("Enter symbol:", placeholder="AAPL, TSLA, PLTR...", key="sidebar_search")
    if quick_symbol and len(quick_symbol.strip()) > 0:
        sym = quick_symbol.upper().strip()
        with st.spinner("Fetching..."):
            data = get_live_price(sym)
        if data["price"] > 0:
            chg_color = "#22c55e" if data["change"]>=0 else "#ef4444"
            arrow = "▲" if data["change"]>=0 else "▼"
            pre = data.get("pre_market",0)
            post = data.get("post_market",0)
            pre_html = f'<div style="font-size:0.65rem;color:#f59e0b;margin-top:2px;">Pre-market: ${pre:.2f}</div>' if pre and pre>0 else ''
            post_html = f'<div style="font-size:0.65rem;color:#a78bfa;margin-top:2px;">After-hours: ${post:.2f}</div>' if post and post>0 else ''
            st.markdown(f"""
            <div style="background:#0d1929;border:1px solid #1e3a5f;border-radius:8px;padding:0.9rem;margin-top:0.4rem;">
                <div style="font-size:0.7rem;color:#64748b;font-family:'Space Mono',monospace;">{data['company']}</div>
                <div style="font-size:1.4rem;font-weight:800;font-family:'Space Mono',monospace;color:#f1f5f9;">${data['price']:.2f}</div>
                <div style="color:{chg_color};font-family:'Space Mono',monospace;font-size:0.85rem;font-weight:700;">{arrow} {abs(data['change']):.2f}%</div>
                <div style="font-size:0.65rem;color:#64748b;margin-top:0.4rem;">H: ${data.get('high',0):.2f} · L: ${data.get('low',0):.2f}</div>
                <div style="font-size:0.65rem;color:#64748b;">Vol: {data.get('volume',0):,}</div>
                {pre_html}{post_html}
            </div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📈 Chart", use_container_width=True, key="qs_chart"):
                    st.session_state.chart_symbol = sym
                    st.rerun()
            with col2:
                if st.button(f"🤖 Ask AI", use_container_width=True, key="qs_ai"):
                    q = f"Tell me everything about {sym} stock today including news and levels"
                    st.session_state.ai_question = q
                    st.session_state.ai_answer = ""
                    st.session_state.chart_symbol = sym
                    st.session_state.pending_question = q
                    st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-header">SAMPLE QUESTIONS</div>', unsafe_allow_html=True)
    samples = [
        "What is Apple stock doing today?",
        "Compare NVDA and AMD",
        "Which stocks are up today?",
        "Any news about Tesla?",
        "What world news affects markets?",
        "Top gainers today?",
        "How is the market overall?",
        "Tell me about Microsoft",
        "Is NVDA a buy right now?",
        "What are support levels for AAPL?",
    ]
    for q in samples:
        if st.button(q, use_container_width=True, key=f"sq_{q}"):
            st.session_state.ai_question = q
            st.session_state.ai_answer = ""
            st.session_state.pending_question = q
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-header">CHART SETTINGS</div>', unsafe_allow_html=True)
    chart_sym_input = st.text_input("Symbol:", value=st.session_state.chart_symbol, key="chart_sym_sidebar")
    if st.button("📈 Update Chart", use_container_width=True):
        st.session_state.chart_symbol = chart_sym_input.upper().strip()
        st.rerun()
    idx_period = PERIOD_OPTIONS.index(st.session_state.chart_period) if st.session_state.chart_period in PERIOD_OPTIONS else 9
    chart_period = st.selectbox("Period:", PERIOD_OPTIONS, index=idx_period, key="chart_period_select")
    if chart_period != st.session_state.chart_period:
        st.session_state.chart_period = chart_period
        st.rerun()
    show_ma = st.checkbox("Moving Averages (MA20/50/200)", value=True)
    show_bb = st.checkbox("Bollinger Bands", value=False)
    show_vol = st.checkbox("Volume bars", value=True)


# ── MARKET OVERVIEW ──
st.markdown('<div class="section-header">MARKET OVERVIEW — Click Details for chart & analysis</div>', unsafe_allow_html=True)
with st.spinner("Loading market indices..."):
    indices = get_index_data()

idx_cols = st.columns(4)
for i, (name, data) in enumerate(indices.items()):
    change = data["change"]
    price = data["price"]
    arrow = "▲" if change>=0 else "▼"
    with idx_cols[i]:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">{name}</div>
            <div class="metric-value">{price:,.2f}</div>
            <div class="metric-change {'up' if change>=0 else 'down'}">{arrow} {abs(change):.2f}%</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Details →", key=f"idx_{name}", use_container_width=True):
            if st.session_state.selected_index == name:
                st.session_state.selected_index = None
            else:
                st.session_state.selected_index = name
                q = f"Tell me about {name} performance today and key drivers"
                st.session_state.ai_question = q
                st.session_state.ai_answer = ""
                st.session_state.pending_question = q
            st.rerun()

if st.session_state.selected_index:
    idx_name = st.session_state.selected_index
    idx_symbol = indices[idx_name]["symbol"]
    with st.expander(f"📊 {idx_name} — Select period below", expanded=True):
        sel_period = st.selectbox("Period:", PERIOD_OPTIONS, index=PERIOD_OPTIONS.index("1mo"), key=f"idx_p_{idx_name}")
        hist_idx = get_chart_data(idx_symbol, sel_period)
        if not hist_idx.empty:
            fig_idx = go.Figure()
            fig_idx.add_trace(go.Scatter(x=hist_idx.index, y=hist_idx['Close'], line=dict(color='#38bdf8',width=2), fill='tozeroy', fillcolor='rgba(56,189,248,0.05)', name=idx_name))
            fig_idx.update_layout(paper_bgcolor='#0a1221',plot_bgcolor='#0a1221',font=dict(family='Space Mono',color='#64748b',size=10),xaxis=dict(gridcolor='#0d1929',color='#475569'),yaxis=dict(gridcolor='#0d1929',color='#475569',side='right',autorange=True),margin=dict(l=10,r=10,t=10,b=10),height=220,showlegend=False)
            st.plotly_chart(fig_idx, use_container_width=True)
        else:
            st.warning("No data for this period.")
        if st.button("✕ Close Chart", key="close_idx"):
            st.session_state.selected_index = None
            st.rerun()

st.markdown("---")

# ── FEAR & GREED + CRYPTO ──
fg_col, crypto_col = st.columns([1,2])
with fg_col:
    st.markdown('<div class="section-header">FEAR & GREED INDEX</div>', unsafe_allow_html=True)
    fg = get_fear_greed()
    val = fg["value"]
    label = fg["label"]
    fg_color = "#ef4444" if val<=25 else "#f97316" if val<=45 else "#f59e0b" if val<=55 else "#84cc16" if val<=75 else "#22c55e"
    st.markdown(f"""<div class="fear-gauge">
        <div style="font-size:2.8rem;font-weight:800;font-family:'Space Mono',monospace;color:{fg_color};">{val}</div>
        <div style="font-size:0.75rem;color:{fg_color};font-family:'Space Mono',monospace;text-transform:uppercase;letter-spacing:2px;margin-bottom:0.5rem;">{label}</div>
        <div style="background:#0a1221;border-radius:20px;height:8px;overflow:hidden;">
            <div style="background:linear-gradient(90deg,#ef4444,#f59e0b,#22c55e);width:{val}%;height:100%;border-radius:20px;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.58rem;color:#475569;font-family:'Space Mono',monospace;margin-top:4px;"><span>Extreme Fear</span><span>Extreme Greed</span></div>
    </div>""", unsafe_allow_html=True)

with crypto_col:
    st.markdown('<div class="section-header">CRYPTO PRICES</div>', unsafe_allow_html=True)
    cryptos = get_crypto_prices()
    if cryptos:
        crypto_cols = st.columns(len(cryptos))
        for i, c in enumerate(cryptos):
            chg_color = "#22c55e" if c["change"]>=0 else "#ef4444"
            arrow = "▲" if c["change"]>=0 else "▼"
            with crypto_cols[i]:
                st.markdown(f"""<div class="metric-card" style="padding:0.8rem;">
                    <div class="metric-label">{c['symbol']} · {c['name']}</div>
                    <div style="font-size:1rem;font-weight:800;font-family:'Space Mono',monospace;color:#f1f5f9;">${c['price']:,.2f}</div>
                    <div style="font-size:0.8rem;font-family:'Space Mono',monospace;color:{chg_color};">{arrow} {abs(c['change']):.2f}%</div>
                </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── MAIN LAYOUT ──
left_col, right_col = st.columns([3,2], gap="large")

with left_col:

    # AI CHAT
    st.markdown('<div class="section-header">ASK STOCKWATCH AI</div>', unsafe_allow_html=True)
    question = st.text_input("Ask anything:", value=st.session_state.ai_question, placeholder="e.g. What is NVDA doing today? Compare Apple and Microsoft...", label_visibility="collapsed", key="ai_input")
    ask_col, clear_col = st.columns([3,1])
    with ask_col:
        ask_clicked = st.button("Ask AI →", type="primary", use_container_width=True)
    with clear_col:
        if st.button("Clear", use_container_width=True):
            st.session_state.ai_question = ""
            st.session_state.ai_answer = ""
            st.rerun()

    # Handle pending questions from sample buttons or news buttons
    pending = st.session_state.get("pending_question", "")
    if pending:
        st.session_state.pending_question = ""
        try:
            from ai_agent import extract_symbols_from_question
            syms = extract_symbols_from_question(pending)
            if syms:
                st.session_state.chart_symbol = syms[0]
        except:
            pass
        with st.spinner("Analyzing real market data..."):
            st.session_state.ai_answer = answer_question(pending)

    if ask_clicked and question.strip():
        st.session_state.ai_question = question
        try:
            from ai_agent import extract_symbols_from_question
            syms = extract_symbols_from_question(question)
            if syms:
                st.session_state.chart_symbol = syms[0]
        except:
            pass
        with st.spinner("Analyzing real market data..."):
            st.session_state.ai_answer = answer_question(question)

    if st.session_state.ai_answer:
        st.markdown(f'<div class="ai-answer">{st.session_state.ai_answer}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # PRICE CHART
    chart_sym = st.session_state.chart_symbol
    chart_per = st.session_state.chart_period
    st.markdown(f'<div class="section-header">PRICE CHART — {chart_sym} · {chart_per}</div>', unsafe_allow_html=True)

    hist = get_chart_data(chart_sym, chart_per)
    if not hist.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index,open=hist['Open'],high=hist['High'],low=hist['Low'],close=hist['Close'],name=chart_sym,increasing_line_color='#22c55e',decreasing_line_color='#ef4444',increasing_fillcolor='rgba(34,197,94,0.2)',decreasing_fillcolor='rgba(239,68,68,0.2)'))
        if show_ma:
            if len(hist)>=20:
                fig.add_trace(go.Scatter(x=hist.index,y=hist['Close'].rolling(20).mean(),line=dict(color='#f59e0b',width=1.5,dash='dot'),name='MA20'))
            if len(hist)>=50:
                fig.add_trace(go.Scatter(x=hist.index,y=hist['Close'].rolling(50).mean(),line=dict(color='#a78bfa',width=1.5,dash='dot'),name='MA50'))
            if len(hist)>=200:
                fig.add_trace(go.Scatter(x=hist.index,y=hist['Close'].rolling(200).mean(),line=dict(color='#6366f1',width=1.5,dash='dot'),name='MA200'))
        if show_bb and len(hist)>=20:
            bb_m = hist['Close'].rolling(20).mean()
            bb_s = hist['Close'].rolling(20).std()
            fig.add_trace(go.Scatter(x=hist.index,y=bb_m+2*bb_s,line=dict(color='#38bdf8',width=1,dash='dash'),name='BB+',opacity=0.6))
            fig.add_trace(go.Scatter(x=hist.index,y=bb_m-2*bb_s,line=dict(color='#38bdf8',width=1,dash='dash'),name='BB-',opacity=0.6,fill='tonexty',fillcolor='rgba(56,189,248,0.03)'))
        if show_vol:
            fig.add_trace(go.Bar(x=hist.index,y=hist['Volume'],name='Vol',marker_color='#1e3a5f',opacity=0.4,yaxis='y2'))
        fig.update_layout(
            paper_bgcolor='#0a1221',plot_bgcolor='#0a1221',
            font=dict(family='Space Mono',color='#64748b',size=10),
            xaxis=dict(gridcolor='#0d1929',showgrid=True,rangeslider=dict(visible=False),color='#475569'),
            yaxis=dict(gridcolor='#0d1929',showgrid=True,color='#475569',side='right',autorange=True),
            yaxis2=dict(overlaying='y',side='left',showgrid=False,color='#1e3a5f',range=[0,hist['Volume'].max()*5]),
            legend=dict(bgcolor='rgba(0,0,0,0)',bordercolor='#1e3a5f',font=dict(color='#94a3b8',size=9),orientation='h',y=1.02),
            margin=dict(l=10,r=10,t=30,b=10),height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No chart data for {chart_sym} at {chart_per} period. Try a longer period.")

    st.markdown("---")

    # SUPPORT & RESISTANCE
    st.markdown(f'<div class="section-header">SUPPORT & RESISTANCE — {chart_sym}</div>', unsafe_allow_html=True)
    levels = get_support_resistance(chart_sym)
    if levels:
        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="support-level"><div class="support-label">52W High</div><div class="support-value up">${levels['high_52w']}</div></div>
            <div class="support-level"><div class="support-label">BB Upper Band</div><div class="support-value" style="color:#38bdf8;">${levels['bb_upper']}</div></div>
            <div class="support-level"><div class="support-label">Resistance 2</div><div class="support-value" style="color:#fbbf24;">${levels['resistance2']}</div></div>
            <div class="support-level" style="border-color:#f97316;"><div class="support-label">🚀 Breakout Level</div><div class="support-value" style="color:#f97316;">${levels['breakout_level']}</div></div>
            """, unsafe_allow_html=True)
        with c2:
            price_vs_ma20 = "above" if levels['current'] > levels['ma20'] else "below"
            price_vs_ma50 = "above" if levels['current'] > levels['ma50'] else "below"
            st.markdown(f"""
            <div class="support-level" style="border-color:#38bdf8;"><div class="support-label">Current Price</div><div class="support-value" style="color:#38bdf8;font-size:1.2rem;">${levels['current']:.2f}</div></div>
            <div class="support-level"><div class="support-label">MA 20 · {price_vs_ma20}</div><div class="support-value" style="color:#f59e0b;">${levels['ma20']}</div></div>
            <div class="support-level"><div class="support-label">MA 50 · {price_vs_ma50}</div><div class="support-value" style="color:#a78bfa;">${levels['ma50']}</div></div>
            <div class="support-level"><div class="support-label">MA 200</div><div class="support-value" style="color:#6366f1;">${levels['ma200']}</div></div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="support-level" style="border-color:#ef4444;"><div class="support-label">⚠️ Breakdown Level</div><div class="support-value" style="color:#ef4444;">${levels['breakdown_level']}</div></div>
            <div class="support-level"><div class="support-label">Support 1</div><div class="support-value" style="color:#22c55e;">${levels['support1']}</div></div>
            <div class="support-level"><div class="support-label">BB Lower Band</div><div class="support-value" style="color:#38bdf8;">${levels['bb_lower']}</div></div>
            <div class="support-level"><div class="support-label">52W Low</div><div class="support-value down">${levels['low_52w']}</div></div>
            """, unsafe_allow_html=True)

        # Expected move + price position
        st.markdown(f"""
        <div class="inst-card" style="margin-top:0.8rem;">
            <div style="font-size:0.6rem;color:#64748b;font-family:'Space Mono',monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">📊 Expected Weekly Move Range (based on volatility)</div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="text-align:center;"><div style="color:#ef4444;font-family:'Space Mono',monospace;font-weight:700;font-size:1rem;">${levels['expected_down']}</div><div style="font-size:0.6rem;color:#475569;">Downside</div></div>
                <div style="color:#64748b;font-size:1.2rem;">↔</div>
                <div style="text-align:center;"><div style="color:#38bdf8;font-family:'Space Mono',monospace;font-weight:700;font-size:1.1rem;">${levels['current']:.2f}</div><div style="font-size:0.6rem;color:#475569;">Current</div></div>
                <div style="color:#64748b;font-size:1.2rem;">↔</div>
                <div style="text-align:center;"><div style="color:#22c55e;font-family:'Space Mono',monospace;font-weight:700;font-size:1rem;">${levels['expected_up']}</div><div style="font-size:0.6rem;color:#475569;">Upside</div></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if levels['resistance1'] != levels['support1']:
            pp = max(0,min(100,(levels['current']-levels['support1'])/(levels['resistance1']-levels['support1'])*100))
        else:
            pp = 50
        pp_label = "Near Resistance" if pp>70 else "Near Support" if pp<30 else "Mid Range"
        pp_color = "#ef4444" if pp>70 else "#22c55e" if pp<30 else "#f59e0b"
        st.markdown(f"""
        <div style="margin-top:0.8rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                <div style="font-size:0.6rem;color:#64748b;font-family:'Space Mono',monospace;text-transform:uppercase;letter-spacing:1px;">Price Position</div>
                <div style="font-size:0.7rem;font-family:'Space Mono',monospace;color:{pp_color};font-weight:700;">{pp_label} · {pp:.0f}%</div>
            </div>
            <div style="background:#0d1929;border-radius:20px;height:10px;overflow:hidden;">
                <div style="background:linear-gradient(90deg,#22c55e,#f59e0b,#ef4444);width:{pp}%;height:100%;border-radius:20px;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.6rem;color:#475569;font-family:'Space Mono',monospace;margin-top:3px;">
                <span>Support ${levels['support1']}</span><span>Resistance ${levels['resistance1']}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # STOCK SCREENER
    st.markdown('<div class="section-header">STOCK SCREENER</div>', unsafe_allow_html=True)
    prices_df, _ = get_stock_data()
    if not prices_df.empty:
        tab1,tab2,tab3,tab4 = st.tabs(["📊 All Stocks","🟢 Top Gainers","🔴 Top Losers","🔥 Most Active"])
        with tab1:
            df_show = prices_df[['symbol','company','price','change_percent','date']].copy()
            df_show.columns = ['Symbol','Company','Price ($)','Change (%)','Date']
            st.dataframe(df_show,use_container_width=True,hide_index=True,height=280)
        with tab2:
            gainers = prices_df[prices_df['change_percent']>0].sort_values('change_percent',ascending=False).head(10)
            for _,row in gainers.iterrows():
                ca,cb,cc,cd = st.columns([1,3,1.5,1.5])
                with ca: st.markdown(f'<span class="ticker-badge">{row["symbol"]}</span>',unsafe_allow_html=True)
                with cb: st.caption(str(row['company'])[:28])
                with cc: st.markdown(f"**${row['price']:.2f}**")
                with cd: st.markdown(f'<span class="up">▲ {row["change_percent"]:.2f}%</span>',unsafe_allow_html=True)
        with tab3:
            with st.spinner("Loading losers..."):
                losers = get_top_losers()
            for row in losers:
                ca,cb,cc = st.columns([1,3,2])
                with ca: st.markdown(f'<span class="ticker-badge">{row["symbol"]}</span>',unsafe_allow_html=True)
                with cb: st.markdown(f"**${row['price']:.2f}**")
                with cc: st.markdown(f'<span class="down">▼ {abs(row["change"]):.2f}%</span>',unsafe_allow_html=True)
        with tab4:
            with st.spinner("Loading most active..."):
                active = get_most_active()
            for row in active[:10]:
                ca,cb,cc,cd = st.columns([1,2,1.5,2])
                with ca: st.markdown(f'<span class="ticker-badge">{row["symbol"]}</span>',unsafe_allow_html=True)
                with cb: st.markdown(f"**${row['price']:.2f}**")
                chg_c = "#22c55e" if row["change"]>=0 else "#ef4444"
                with cc: st.markdown(f'<span style="color:{chg_c};font-family:Space Mono,monospace;font-size:0.8rem;">{"▲" if row["change"]>=0 else "▼"}{abs(row["change"]):.2f}%</span>',unsafe_allow_html=True)
                with cd: st.caption(f'Vol: {row["volume"]:,}')
    else:
        st.info("No stock data. Click Refresh Market Data.")


with right_col:

    # SECTOR PERFORMANCE
    st.markdown('<div class="section-header">SECTOR PERFORMANCE</div>', unsafe_allow_html=True)
    with st.spinner("Loading sectors..."):
        sector_data = get_sector_data()
    if sector_data:
        sector_df = pd.DataFrame(sector_data).sort_values("Avg Change",ascending=True)
        colors = ['#22c55e' if x>=0 else '#ef4444' for x in sector_df['Avg Change']]
        text_colors = ['#22c55e' if x>=0 else '#ef4444' for x in sector_df['Avg Change']]
        fig2 = go.Figure(go.Bar(
            x=sector_df['Avg Change'],y=sector_df['Sector'],orientation='h',
            marker_color=colors,
            text=[f"{v:+.2f}%" for v in sector_df['Avg Change']],
            textposition='outside',
            textfont=dict(family='Space Mono',size=11,color=text_colors)
        ))
        fig2.update_layout(
            paper_bgcolor='#0a1221',plot_bgcolor='#0a1221',
            font=dict(family='Space Mono',color='#64748b',size=10),
            xaxis=dict(gridcolor='#0d1929',color='#475569',zeroline=True,zerolinecolor='#1e3a5f'),
            yaxis=dict(color='#94a3b8',gridcolor='#0d1929'),
            margin=dict(l=10,r=70,t=10,b=10),height=280,showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # WORLD NEWS
    st.markdown('<div class="section-header">MARKET INTELLIGENCE — Click to read & analyze</div>', unsafe_allow_html=True)
    world_news = get_world_news()
    category_labels = {"federal reserve interest rates":"Fed","US economy inflation":"Economy","stock market today":"Markets","global economy":"Global","oil prices energy":"Energy"}
    seen_titles = set()
    if not world_news.empty:
        count = 0
        for idx, row in world_news.iterrows():
            if count >= 10: break
            title = str(row.get('title',''))
            if not title or title=='nan' or '[Removed]' in title: continue
            if title in seen_titles: continue
            seen_titles.add(title)
            desc = str(row.get('description',''))
            source = str(row.get('source',''))
            category = category_labels.get(str(row.get('category','')),str(row.get('category',''))[:8])
            published = str(row.get('published_at',''))[:10]
            short_title = title[:85]+('...' if len(title)>85 else '')
            with st.expander(f"{short_title}"):
                st.markdown(f'<span class="news-category">{category}</span><span style="font-size:0.68rem;color:#475569;font-family:Space Mono,monospace;">{source} · {published}</span>',unsafe_allow_html=True)
                if desc and desc!='nan' and desc!='None':
                    st.markdown(f'<div class="news-desc">{desc}</div>',unsafe_allow_html=True)
                if st.button(f"🤖 How does this affect stocks?", key=f"wn_ai_{idx}"):
                    q = f"How does this news affect US stocks and market: {title}"
                    st.session_state.ai_question = q
                    st.session_state.ai_answer = ""
                    st.session_state.pending_question = q
                    st.rerun()
            count += 1
    else:
        st.info("No news. Click Refresh Market Data.")

    st.markdown("---")

    # STOCK NEWS
    st.markdown('<div class="section-header">STOCK NEWS — Click to read & analyze</div>', unsafe_allow_html=True)
    _, stock_news = get_stock_data()
    seen_stock_titles = set()
    if not stock_news.empty:
        count = 0
        for idx, row in stock_news.iterrows():
            if count >= 10: break
            title = str(row.get('title',''))
            if not title or title=='nan' or '[Removed]' in title: continue
            if title in seen_stock_titles: continue
            seen_stock_titles.add(title)
            desc = str(row.get('description',''))
            symbol = str(row.get('symbol',''))
            source = str(row.get('source',''))
            short_title = title[:75]+('...' if len(title)>75 else '')
            with st.expander(f"[{symbol}] {short_title}"):
                st.markdown(f'<span class="ticker-badge">{symbol}</span><span style="font-size:0.68rem;color:#475569;font-family:Space Mono,monospace;">{source}</span>',unsafe_allow_html=True)
                if desc and desc!='nan' and desc!='None':
                    st.markdown(f'<div class="news-desc">{desc}</div>',unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📈 Chart {symbol}", key=f"sn_chart_{idx}"):
                        st.session_state.chart_symbol = symbol
                        st.rerun()
                with col_b:
                    if st.button(f"🤖 Ask AI", key=f"sn_ai_{idx}"):
                        q = f"Tell me about {symbol} stock and this news: {title}"
                        st.session_state.ai_question = q
                        st.session_state.ai_answer = ""
                        st.session_state.chart_symbol = symbol
                        st.session_state.pending_question = q
                        st.rerun()
            count += 1

# FOOTER
st.markdown("---")
st.markdown(f"""<div style="text-align:center;color:#1e3a5f;font-family:'Space Mono',monospace;font-size:0.65rem;padding:0.8rem;">
STOCKWATCH AI · Python · Streamlit · Groq LLaMA 3.3 · Yahoo Finance · NewsAPI · 
{now_local.strftime("%Y-%m-%d %H:%M")} · For informational purposes only. Not financial advice.
</div>""", unsafe_allow_html=True)
