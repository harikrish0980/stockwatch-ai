import yfinance as yf
import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Top 50 US stocks we will track
STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "JNJ", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
    "KO", "AVGO", "COST", "MCD", "WMT", "BAC", "DIS", "CSCO", "XOM",
    "ADBE", "CRM", "NFLX", "AMD", "INTC", "QCOM", "TXN", "AMGN", "UNH",
    "LLY", "TMO", "DHR", "NEE", "PM", "RTX", "HON", "UPS", "CAT",
    "GS", "MS", "BLK", "SPGI", "AXP"
]

def collect_stock_prices():
    conn = sqlite3.connect("stockwatch.db")
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    print("Collecting stock prices...")
    
    for symbol in STOCKS:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            open_price = info.get("regularMarketOpen", 0)
            high = info.get("dayHigh", 0)
            low = info.get("dayLow", 0)
            volume = info.get("regularMarketVolume", 0)
            prev_close = info.get("regularMarketPreviousClose", 0)
            company = info.get("shortName", symbol)
            
            # Calculate change percent
            if prev_close and prev_close != 0:
                change_percent = ((price - prev_close) / prev_close) * 100
            else:
                change_percent = 0
            
            cursor.execute("""
                INSERT INTO stock_prices 
                (symbol, company, price, open, high, low, volume, change_percent, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol, company, price, open_price, high, low, volume, change_percent, today))
            
            print(f"✓ {symbol} - ${price:.2f} ({change_percent:.2f}%)")
            
        except Exception as e:
            print(f"✗ {symbol} - Error: {e}")
    
    conn.commit()
    conn.close()
    print("Stock prices collected!\n")

def collect_stock_news(symbol):
    try:
        url = f"https://newsapi.org/v2/everything?q={symbol}+stock&language=en&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        conn = sqlite3.connect("stockwatch.db")
        cursor = conn.cursor()
        
        if data.get("articles"):
            for article in data["articles"]:
                cursor.execute("""
                    INSERT INTO stock_news (symbol, title, description, source, url, published_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    article.get("title", ""),
                    article.get("description", ""),
                    article.get("source", {}).get("name", ""),
                    article.get("url", ""),
                    article.get("publishedAt", "")
                ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"News error for {symbol}: {e}")

def collect_world_news():
    print("Collecting world news...")
    
    # Topics that affect stock markets
    topics = [
        "federal reserve interest rates",
        "US economy inflation",
        "stock market today",
        "global economy",
        "oil prices energy"
    ]
    
    conn = sqlite3.connect("stockwatch.db")
    cursor = conn.cursor()
    
    for topic in topics:
        try:
            url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
            response = requests.get(url)
            data = response.json()
            
            if data.get("articles"):
                for article in data["articles"]:
                    cursor.execute("""
                        INSERT INTO world_news (title, description, source, url, category, published_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        article.get("title", ""),
                        article.get("description", ""),
                        article.get("source", {}).get("name", ""),
                        article.get("url", ""),
                        topic,
                        article.get("publishedAt", "")
                    ))
            
            print(f"✓ World news collected for: {topic}")
            
        except Exception as e:
            print(f"World news error: {e}")
    
    conn.commit()
    conn.close()
    print("World news collected!\n")

def run_collection():
    print(f"\n=== StockWatch AI - Data Collection Started ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    collect_stock_prices()
    
    # Collect news for first 10 stocks only (free tier limit)
    print("Collecting stock news...")
    for symbol in STOCKS[:10]:
        collect_stock_news(symbol)
        print(f"✓ News collected for {symbol}")
    
    collect_world_news()
    
    print("=== Collection Complete ===\n")

if __name__ == "__main__":
    run_collection()