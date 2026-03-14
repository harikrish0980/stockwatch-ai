import sqlite3

def create_database():
    conn = sqlite3.connect("stockwatch.db")
    cursor = conn.cursor()

    # Table for stock prices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            company TEXT,
            price REAL,
            open REAL,
            high REAL,
            low REAL,
            volume INTEGER,
            change_percent REAL,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for stock news
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            title TEXT,
            description TEXT,
            source TEXT,
            url TEXT,
            published_at TEXT,
            sentiment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for world news
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            source TEXT,
            url TEXT,
            category TEXT,
            published_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()
    create_database()