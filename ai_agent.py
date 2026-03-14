import sqlite3
import pandas as pd
import yfinance as yf
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Company name to symbol mapping
COMPANY_MAP = {
    "AMAZON": "AMZN",
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "GOOGLE": "GOOGL",
    "ALPHABET": "GOOGL",
    "TESLA": "TSLA",
    "META": "META",
    "FACEBOOK": "META",
    "NETFLIX": "NFLX",
    "NVIDIA": "NVDA",
    "PALANTIR": "PLTR",
    "DISNEY": "DIS",
    "WALMART": "WMT",
    "NIKE": "NKE",
    "UBER": "UBER",
    "AIRBNB": "ABNB",
    "SPOTIFY": "SPOT",
    "SNAPCHAT": "SNAP",
    "INTEL": "INTC",
    "SALESFORCE": "CRM",
    "ORACLE": "ORCL",
    "ADOBE": "ADBE",
    "PAYPAL": "PYPL",
    "COINBASE": "COIN",
    "ROBINHOOD": "HOOD",
    "GOLDMAN": "GS",
    "JPMORGAN": "JPM",
    "BERKSHIRE": "BRK-B",
    "JOHNSON": "JNJ",
    "VISA": "V",
    "MASTERCARD": "MA",
    "CHEVRON": "CVX",
    "EXXON": "XOM",
    "COSTCO": "COST",
    "MCDONALDS": "MCD",
    "COCA COLA": "KO",
    "PEPSI": "PEP",
    "BROADCOM": "AVGO",
    "HOME DEPOT": "HD",
    "BLACKROCK": "BLK",
    "AMERICAN EXPRESS": "AXP",
    "MORGAN STANLEY": "MS",
    "QUALCOMM": "QCOM",
    "TEXAS INSTRUMENTS": "TXN",
    "AMGEN": "AMGN",
    "UNITEDHEALTH": "UNH",
    "ELI LILLY": "LLY",
    "THERMO FISHER": "TMO",
    "CATERPILLAR": "CAT",
    "HONEYWELL": "HON",
    "UPS": "UPS",
    "RAYTHEON": "RTX",
    "PHILIP MORRIS": "PM",
    "NEXTERA": "NEE",
    "DANAHER": "DHR",
    "SPGI": "SPGI",
    "CISCO": "CSCO",
    "ABBVIE": "ABBV",
    "MERCK": "MRK",
}

def fetch_live_stock(symbol):
    try:
        # Handle symbols with dashes like BRK-B
        stock = yf.Ticker(symbol)
        info = stock.info

        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")

        if not price:
            return f"Could not fetch price for {symbol}. Market may be closed or symbol may be invalid."

        prev_close = info.get("regularMarketPreviousClose", 0)
        change_percent = ((price - prev_close) / prev_close) * 100 if prev_close else 0
        company = info.get("shortName", symbol)
        high = info.get("dayHigh", 0)
        low = info.get("dayLow", 0)
        volume = info.get("regularMarketVolume", 0)
        market_cap = info.get("marketCap", 0)
        fifty_two_week_high = info.get("fiftyTwoWeekHigh", 0)
        fifty_two_week_low = info.get("fiftyTwoWeekLow", 0)
        market_state = info.get("marketState", "Unknown")

        return f"""
        LIVE DATA FOR {symbol}:
        Company: {company}
        Market State: {market_state}
        Current Price: ${price:.2f}
        Change Today: {change_percent:.2f}%
        Day High: ${high:.2f}
        Day Low: ${low:.2f}
        Volume: {volume:,}
        Market Cap: ${market_cap:,}
        52 Week High: ${fifty_two_week_high:.2f}
        52 Week Low: ${fifty_two_week_low:.2f}
        """
    except Exception as e:
        return f"Could not fetch data for {symbol}. It may be an invalid symbol. Error: {e}"

def extract_symbols_from_question(question):
    upper_question = question.upper()
    found_symbols = []

    # Check company names first
    for company, symbol in COMPANY_MAP.items():
        if company in upper_question:
            found_symbols.append(symbol)

    # If found via company name return them
    if found_symbols:
        return list(set(found_symbols))

    # Try to extract stock symbols directly
    words = upper_question.split()
    common_words = [
        "WHAT", "IS", "THE", "FOR", "ABOUT", "STOCK", "PRICE",
        "TODAY", "NEWS", "HOW", "TELL", "ME", "AND", "OF", "A",
        "ARE", "UP", "DOWN", "BEST", "WORST", "LATEST", "CURRENT",
        "GIVE", "SHOW", "FIND", "GET", "ANY", "ALL", "TOP", "LOW",
        "HIGH", "MARKET", "WORLD", "GLOBAL", "US", "USA", "PERFORMING",
        "DOING", "LOOKING", "FEELS", "THINK", "STOCKS", "COMPARE",
        "BETWEEN", "VS", "VERSUS", "WHICH", "THAT", "THIS", "THESE",
        "THOSE", "THEIR", "THERE", "THEY", "WILL", "WOULD", "COULD",
        "SHOULD", "HAVE", "HAS", "HAD", "BEEN", "BEING", "BE",
        "DO", "DOES", "DID", "WITH", "FROM", "INTO", "THROUGH",
        "DURING", "BEFORE", "AFTER", "ABOVE", "BELOW", "BETWEEN",
        "GAIN", "GAINER", "GAINERS", "LOSER", "LOSERS", "PERFORM",
        "PERFORMANCE", "REPORT", "EARNINGS", "QUARTER", "ANNUAL"
    ]

    for word in words:
        clean = re.sub(r'[^A-Z\-]', '', word)
        if 2 <= len(clean) <= 6 and clean not in common_words:
            found_symbols.append(clean)

    return list(set(found_symbols)) if found_symbols else []

def get_stock_data(symbol=None):
    try:
        conn = sqlite3.connect("stockwatch.db")

        if symbol:
            prices = pd.read_sql(f"""
                SELECT symbol, company, price, change_percent, high, low, volume, date 
                FROM stock_prices 
                WHERE symbol = '{symbol.upper()}'
                ORDER BY date DESC LIMIT 5
            """, conn)

            news = pd.read_sql(f"""
                SELECT title, description, source, published_at 
                FROM stock_news 
                WHERE symbol = '{symbol.upper()}'
                ORDER BY published_at DESC LIMIT 10
            """, conn)
        else:
            prices = pd.read_sql("""
                SELECT symbol, company, price, change_percent, date 
                FROM stock_prices 
                ORDER BY date DESC, change_percent DESC LIMIT 20
            """, conn)

            news = pd.read_sql("""
                SELECT symbol, title, description, source, published_at 
                FROM stock_news 
                ORDER BY published_at DESC LIMIT 20
            """, conn)

        conn.close()
        return prices, news

    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_world_news():
    try:
        conn = sqlite3.connect("stockwatch.db")
        world_news = pd.read_sql("""
            SELECT title, description, category, source, published_at 
            FROM world_news 
            ORDER BY published_at DESC LIMIT 20
        """, conn)
        conn.close()
        return world_news
    except Exception as e:
        print(f"World news error: {e}")
        return pd.DataFrame()

def answer_question(user_question):
    try:
        # Get all known symbols from database
        conn = sqlite3.connect("stockwatch.db")
        symbols_df = pd.read_sql("SELECT DISTINCT symbol FROM stock_prices", conn)
        conn.close()
        known_symbols = symbols_df["symbol"].tolist()
    except:
        known_symbols = []

    # Extract symbols from question
    detected_symbols = extract_symbols_from_question(user_question)

    # Check which ones are in our database
    db_symbols = [s for s in detected_symbols if s in known_symbols]
    live_symbols = [s for s in detected_symbols if s not in known_symbols]

    # Get data from database
    all_prices = pd.DataFrame()
    all_news = pd.DataFrame()

    if db_symbols:
        for symbol in db_symbols:
            prices, news = get_stock_data(symbol)
            all_prices = pd.concat([all_prices, prices], ignore_index=True)
            all_news = pd.concat([all_news, news], ignore_index=True)
    else:
        # General question - get all stocks
        all_prices, all_news = get_stock_data()

    # Fetch live data for symbols not in database
    live_data = ""
    for symbol in live_symbols:
        print(f"Fetching live data for {symbol}...")
        live_data += fetch_live_stock(symbol) + "\n"

    # Get world news
    world_news = get_world_news()

    # Handle empty database gracefully
    db_empty = all_prices.empty and not live_data
    if db_empty:
        db_context = "No stock data in database yet. Please refresh data."
    else:
        db_context = all_prices.to_string() if not all_prices.empty else "No database data for this stock."

    # Build full context
    context = f"""
    STOCK DATA FROM DATABASE:
    {db_context}

    LIVE FETCHED DATA:
    {live_data if live_data else "No live data fetched."}

    LATEST STOCK NEWS:
    {all_news.to_string() if not all_news.empty else "No news available."}

    WORLD NEWS AFFECTING MARKETS:
    {world_news.to_string() if not world_news.empty else "No world news available."}
    """

    prompt = f"""
    You are StockWatch AI, a financial intelligence assistant.

    You have access to real current stock data and news.
    Use ONLY this data to answer questions.
    Be specific with actual numbers and news titles when relevant.
    Keep answers clear and useful for investors.
    If data is not available, say so clearly and suggest the user refresh data.
    Never make up numbers or prices.
    If market is closed, mention that prices shown are from last close.

    REAL DATA:
    {context}

    USER QUESTION: {user_question}

    Answer based on the real data above:
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"AI service error: {e}. Please try again."

if __name__ == "__main__":
    print("\n=== StockWatch AI Agent ===")
    print("Ask anything about US stocks. Type 'exit' to quit.\n")

    while True:
        question = input("Your question: ")
        if question.lower() == "exit":
            break
        print("\nThinking...\n")
        answer = answer_question(question)
        print(f"Answer: {answer}\n")
