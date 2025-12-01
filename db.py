#Flask
from flask import g

#Databases
import sqlite3, os, hashlib, base64

def get_database():
    if 'db' not in g:
        dbpath = "database.db"
        if not os.path.exists(dbpath):
            create_database()
        g.db = sqlite3.connect("database.db")
        g.db.row_factory = sqlite3.Row

        print("Connected to database!")
    return g.db

def create_database(db_path="database.db"):
    """
    Creates a new SQLite database using the schema defined in the DBML specification.
    All relationships and constraints are included where supported by SQLite.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # === USERS ===
    cursor.execute("""
    CREATE TABLE Users (
        username TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        tag TEXT
    );
    """)

    # === VIDEOS ===
    cursor.execute("""
    CREATE TABLE Videos (
        vidID TEXT PRIMARY KEY,
        postID INTEGER UNIQUE,  -- link to Posts
        title TEXT,
        duration INTEGER,
        published TEXT,          
        description TEXT,
        thumbnailsdefault TEXT,
        thumbnailsmedium TEXT,
        thumbnailshigh TEXT,
        thumbnailsmax TEXT,
        kind TEXT,
        channelid TEXT,           
        csr INTEGER,
        gamemap TEXT,
        gamemode TEXT,
        videotype TEXT,
        etag TEXT,
        FOREIGN KEY(postID) REFERENCES Posts(postID) ON DELETE CASCADE
    );
    """)

    # === MESSAGES ===
    cursor.execute("""
    CREATE TABLE Messages (
        msgID INTEGER PRIMARY KEY AUTOINCREMENT,
        boardID INTEGER,
        username TEXT NOT NULL,
        datetime TEXT,
        FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE,
        FOREIGN KEY (boardID) REFERENCES Forums(boardID) ON DELETE CASCADE
    );
    """)

    # === REPORTS ===
    cursor.execute("""
    CREATE TABLE Reports (
        reportID INTEGER PRIMARY KEY AUTOINCREMENT,
        msgID INTEGER NOT NULL,
        FOREIGN KEY (msgID) REFERENCES Messages(msgID) ON DELETE CASCADE
    );
    """)

    # === ARTICLES ===
    cursor.execute("""
    CREATE TABLE Articles (
        articleID INTEGER PRIMARY KEY AUTOINCREMENT,
        postID INTEGER UNIQUE,
        title TEXT,
        description TEXT,
        content TEXT,
        image_filename TEXT,
        FOREIGN KEY(postID) REFERENCES Posts(postID) ON DELETE CASCADE
    );
    """)

    # === FORUMS ===
    cursor.execute("""
    CREATE TABLE Forums (
        forumID INTEGER PRIMARY KEY AUTOINCREMENT,
        postID INTEGER UNIQUE,
        originalPoster TEXT,
        FOREIGN KEY(postID) REFERENCES Posts(postID)
    );
    """)

    # === POSTS ===
    cursor.execute("""
    CREATE TABLE Posts (
        postID INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT
    );
    """)

        # Content Linking table for all articles / videos using preset tags
    cursor.execute(""" 
    CREATE TABLE Tags (
        tagName STRING PRIMARY KEY
        );
    """)

    cursor.execute("""
        CREATE TABLE PostTags (
        postID INTEGER,
        tagName TEXT,
        PRIMARY KEY (postID, tagName),
        FOREIGN KEY (postID) REFERENCES Posts(postID) ON DELETE CASCADE,
        FOREIGN KEY (tagName) REFERENCES Tags(tagName) ON DELETE CASCADE
        ); 
    """)


    # === RELATIONSHIPS ===
    # Messages.boardID → Posts.postID
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_messages_boardID ON Messages(boardID);
    """)

    # == Triggers ===
    #video table row additions
    cursor.execute("""
        CREATE TRIGGER videos_post_insert
        AFTER INSERT ON Videos
        FOR EACH ROW
        BEGIN
            INSERT INTO Posts(date)
            VALUES (NEW.published);
            
            -- Update the newly inserted video row to link to the post
            UPDATE Videos
            SET postID = (SELECT last_insert_rowid())
            WHERE vidID = NEW.vidID;
        END;
                      
    """)

    #article table row additions
    cursor.execute("""
        CREATE TRIGGER articles_post_insert
        AFTER INSERT ON Articles
        FOR EACH ROW
        BEGIN
            INSERT INTO Posts(date)
            VALUES (datetime('now'));
            
            -- Update the newly inserted article row to link to the post
            UPDATE Articles
            SET postID = (SELECT last_insert_rowid())
            WHERE articleID = NEW.articleID;
        END;
                      
    """)

    #article table row additions
    cursor.execute("""
        CREATE TRIGGER forum_post_insert
        AFTER INSERT ON Forums
        FOR EACH ROW
        BEGIN
            INSERT INTO Posts(date)
            VALUES (datetime('now'));
            
            -- Update the newly inserted article row to link to the post
            UPDATE Articles
            SET postID = (SELECT last_insert_rowid())
            WHERE articleID = NEW.articleID;
        END;
                      
    """)

    conn.commit()
    conn.close()
    print("Database created successfully.")


dbpath = "database.db"
if not os.path.exists(dbpath):
    create_database()

