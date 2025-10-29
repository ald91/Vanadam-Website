import sqlite3

def create_database(db_path="database.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        username TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        tag TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Videos (
        vidID INTEGER PRIMARY KEY AUTOINCREMENT,
        vidType TEXT,
        date TEXT,
        game TEXT,
        mmr INTEGER,
        map TEXT,
        mode TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Message (
        msgID INTEGER PRIMARY KEY AUTOINCREMENT,
        board TEXT,
        username TEXT NOT NULL,
        datetime TEXT,
        FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Report (
        reportID INTEGER PRIMARY KEY AUTOINCREMENT,
        msgID INTEGER NOT NULL,
        FOREIGN KEY (msgID) REFERENCES Message(msgID) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Article (
        articleID INTEGER PRIMARY KEY AUTOINCREMENT,
        tags TEXT,
        date TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Tables created successfully.")
