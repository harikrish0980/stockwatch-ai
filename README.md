# StockWatch AI 📡

I built this because I wanted to understand what's happening in the stock market without paying for expensive tools. Everything here runs on free APIs and open source libraries.

It lets you type a question like "what's happening with Nvidia today?" and get a real answer based on actual live data — not a guess.

---

## What it does

You get a dashboard that shows live market data, news, and charts. You can ask questions in plain English and the AI pulls real prices and news before answering. That's the RAG part — it reads real data first, then talks.

The main things:

- Market overview — S&P 500, NASDAQ, DOW, VIX updating live
- Ask any question about any stock and get a real answer
- Candlestick charts with moving averages and Bollinger Bands
- Support and resistance levels so you know where price might bounce or break
- Fear & Greed index so you know if the market is panicking or euphoric
- Crypto prices — BTC, ETH, SOL
- News from around the world with AI analysis
- Stock screener — who's up, who's down, who's most traded
- Watchlist for your own stocks

---

## How it actually works

When you ask "how is Apple doing?", the app:
1. Pulls Apple's real price and news from the database
2. Sends that real data to the AI
3. AI reads the actual numbers and answers

That's RAG. The AI isn't guessing — it's reading real data before it talks.

---

## What I used

- Python and Streamlit for the app
- Groq + LLaMA 3.3 as the AI brain — completely free
- Yahoo Finance for live stock prices — completely free
- NewsAPI for market news — free tier
- SQLite as the database
- Plotly for the charts

Total cost to run this: zero dollars.

---

## Running it yourself

You need two free API keys:
- Groq: console.groq.com
- NewsAPI: newsapi.org

Then:
```bash
git clone https://github.com/harikrish0980/stockwatch-ai.git
cd stockwatch-ai
pip install streamlit pandas groq python-dotenv yfinance newsapi-python requests plotly pytz
```

Create a `.env` file:
```
GROQ_API_KEY=your_key
NEWS_API_KEY=your_key
```

Then run:
```bash
python setupDB.py
python collector.py
python -m streamlit run Stockwatch_ai_app.py
```

---

## Project files

- `Stockwatch_ai_app.py` — the whole web app
- `ai_agent.py` — the RAG agent that answers questions
- `collector.py` — pulls stock prices and news daily
- `setupDB.py` — sets up the database

## I have Personalize It

The app is built so one can make it self:

**Watchlist** — add any stocks to follow daily. They show up in the sidebar with live prices every time open the app.

**Chart settings** — pick your default symbol and time period from the sidebar. Change it anytime — 1 minute charts for day trading or 1 year charts for long term.

**Quick search** — type any ticker in the sidebar to instantly see price, change, high, low and volume without leaving the page.

**Sample questions** — the sidebar has preset questions but you can type anything in the AI box. Ask about your specific stocks, compare two companies, or ask what's driving the market today.

**Chart overlays** — toggle moving averages (MA20/50/200) and Bollinger Bands on or off depending on what you need to see.

**Index details** — click any index card (S&P 500, NASDAQ etc.) and pick your own time period to see that index's chart.

**News AI analysis** — click any news headline and hit "How does this affect stocks?" to get AI analysis specific to that news.
```