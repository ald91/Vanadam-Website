#Flask
from flask import g

#Databases
import sqlite3, os, hashlib, base64

# get relative path name
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "database.db")

def get_database():
    os.makedirs(base_dir, exist_ok=True) #make sure the directory is a thing

    if 'db' not in g:
        if not os.path.exists(db_path):
            create_database(db_path)                       

        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
        print(f"Connected to database at: {db_path}")
    return g.db

def create_database(db_path):
    
    """ Creates a new SQLite database using the schema defined in the DBML specification.
        All relationships and constraints are included where supported by SQLite.  """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # === USERS ===
    cursor.execute("""
    CREATE TABLE Users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        xboxname TEXT,
        arenarank TEXT,
        timezone TEXT,
        userTags TEXT,
        isAdmin BOOLEAN default 0,
        banned BOOLEAN default 0        
    );
    """)

    
    # === POSTS ===
    cursor.execute("""
    CREATE TABLE Posts (
        postID INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK (type IN ('article', 'video')),
        date TEXT DEFAULT (datetime('now'))
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
        hidden BOOLEAN default 0,
        manualedit BOOLEAN default 0,
        etag TEXT,
        FOREIGN KEY(postID) REFERENCES Posts(postID) ON DELETE CASCADE
    );
    """)

    # === FORUMS ===
    cursor.execute("""
        CREATE TABLE Forums (
            forumID INTEGER PRIMARY KEY AUTOINCREMENT,
            originalPoster TEXT,
            title TEXT,
            content TEXT,
            date TEXT DEFAULT (datetime('now'))
        );
        """)

    # === MESSAGES ===
    cursor.execute("""
    CREATE TABLE Messages (
        msgID INTEGER PRIMARY KEY AUTOINCREMENT,
        forumID INTEGER,
        username TEXT NOT NULL,
        content TEXT NOT NULL,
        date TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (forumID) REFERENCES Forums(forumID) ON DELETE CASCADE
    );
    """)

    # === REPORTS ===
    cursor.execute("""
    CREATE TABLE Reports (
        reportID INTEGER PRIMARY KEY AUTOINCREMENT,
        target_id INTEGER NOT NULL,
        reported_by TEXT NOT NULL,
        reason TEXT,
        date TEXT DEFAULT (datetime('now'))
    );
    """)

    # === ARTICLES ===
    cursor.execute("""
    CREATE TABLE Articles (
        articleID INTEGER PRIMARY KEY AUTOINCREMENT,
        postID INTEGER UNIQUE,
        title TEXT,
        description TEXT,
        json_filename TEXT,
        image_filename TEXT,
        hidden BOOLEAN default 0,
        FOREIGN KEY(postID) REFERENCES Posts(postID) ON DELETE CASCADE
    );
    """)

    # === MAPS ===
    cursor.execute("""
    CREATE TABLE Maps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mapName TEXT NOT NULL UNIQUE,
        description TEXT,
        ranked_arena BOOLEAN DEFAULT 0,
        europeanHaloLeague BOOLEAN DEFAULT 0,
        HaloChampionshipSeries BOOLEAN DEFAULT 0
    );
    """)

    # === GAME MODES ===
    cursor.execute("""
    CREATE TABLE game_modes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code INTEGER NOT NULL UNIQUE,
        name TEXT NOT NULL
    );
    """)

    # === PLAYLISTS ===
    cursor.execute("""
    CREATE TABLE playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    # === Playists to Map and Mode Joining Table ===
    cursor.execute("""
    CREATE TABLE playlist_map_modes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER NOT NULL,
        map_id INTEGER NOT NULL,
        mode_id INTEGER NOT NULL,
        FOREIGN KEY (playlist_id) REFERENCES playlists(id),
        FOREIGN KEY (map_id) REFERENCES maps(id),
        FOREIGN KEY (mode_id) REFERENCES game_modes(id)
    );
    """)



    # Content Linking table for all articles / videos using preset tags
    cursor.execute(""" 
    CREATE TABLE Tags (
        tagName TEXT PRIMARY KEY
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

    #coaching requests table
    cursor.execute("""
        CREATE TABLE CoachingRequests (
        crequestID   INTEGER PRIMARY KEY AUTOINCREMENT,
        crequestTime TEXT DEFAULT CURRENT_TIMESTAMP,
        -- user-facing fields
        userID       INTEGER NOT NULL DEFAULT 0,
        username     TEXT,
        email        TEXT,
        xboxname     TEXT,
        arenarank    TEXT,
        sessiontype  TEXT NOT NULL,
        coach        TEXT,
        agreeddate   TEXT,
        agreedtime   TEXT,
        delivered    BOOLEAN NOT NULL DEFAULT 0,
        paid         BOOLEAN NOT NULL DEFAULT 0,
        -- admin-only fields
        invoiceID    TEXT NOT NULL DEFAULT 'no document'
        );
        """ )    
    
     # === YT Requests ===
    cursor.execute("""
    CREATE TABLE YTRequests (
        YTrequestID     INTEGER PRIMARY KEY AUTOINCREMENT,
        YTrequestTime   TEXT DEFAULT CURRENT_TIMESTAMP,
        userID          INTEGER NOT NULL,
        username        TEXT NOT NULL,  
        xboxname        TEXT NOT NULL,
        arenarank       TEXT NOT NULL,
        videoURL        TEXT NOT NULL,
        playlist        TEXT NOT NULL,
        matchmap        TEXT NOT NULL,
        matchgamemode   TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'recieved',
        trackernetwork  TEXT,
        youtubevideoID  TEXT,  
        
        FOREIGN KEY (userID) REFERENCES Users(userID) ON DELETE CASCADE    
        );
        """)

    # === RELATIONSHIPS ===
    # Messages.forumID → Posts.forumID
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_messages_boardID ON Messages(forumID);
    """)

    #Create a composite key on reports so that one user may not report the same element multiple times, spam prevention
    cursor.execute("""
    CREATE UNIQUE INDEX idx_unique_report
    ON Reports (target_id, reported_by);
    """)



    # == Triggers ===
    # video table row additions
#    cursor.execute("""
#        CREATE TRIGGER videos_post_insert
#        AFTER INSERT ON Videos
#        FOR EACH ROW
#        BEGIN
#            -- Update the newly inserted video row to link to the post
#            UPDATE Videos
#            SET postID = (SELECT last_insert_rowid())
#            WHERE vidID = NEW.vidID;
#        END;                      
#    """)
#
#    #article table row additions
#    cursor.execute("""
#        CREATE TRIGGER articles_post_insert
#        AFTER INSERT ON Articles
#        FOR EACH ROW
#        BEGIN
#            -- Update the newly inserted article row to link to the post
#            UPDATE Articles
#            SET postID = (SELECT last_insert_rowid())
#            WHERE articleID = NEW.articleID;
#        END;
#                      
#    """)

    conn.commit()
    conn.close()
    print("Database created successfully.")

if not os.path.exists(db_path):
    create_database(db_path)



