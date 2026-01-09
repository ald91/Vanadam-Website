from ..data.db import get_database
from app.forms import SearchForm

def fetchSideBar() -> list[dict]:
    
    """fetches records from DB for the home page right side bar area"""

    results = (4,)

    db = get_database()
    cur = db.cursor()

    videosQuery= """
    SELECT vidID, title, published, thumbnailsdefault
    FROM Videos
    WHERE videotype != 'Livestream'
    ORDER BY published DESC
    LIMIT ?; """


    cur.execute(videosQuery, results)
    videos = cur.fetchall()
    videos = [dict(row) for row in videos]

    return videos

def fetchNewsBar() -> list[dict]:

    """fetches records from DB for the home page bottom area"""

    db = get_database()
    cur = db.cursor()
    params = ('discussion', 'map guide', 'news',  #video params
                8) # number of items

    newsquery = """
    SELECT *
    FROM (
        SELECT 'Video' AS type, v.postID, v.vidID, v.title, v.thumbnailsmax, v.description, p.date
        FROM Videos v
        JOIN Posts p on v.postID = p.postID
        JOIN PostTags pt ON v.postID = pt.postID
        WHERE pt.tagName IN (?, ?, ?)

        UNION ALL

        SELECT 'Article' AS type, a.postID, a.articleID, a.title, a.image_filename, a.description, p.date
        FROM Articles a
        JOIN Posts p on a.postID = p.postID
        JOIN PostTags pt ON a.postID = pt.postID
    )
    ORDER BY date DESC
    LIMIT ?;
    """

    cur.execute(newsquery, params)
    news = cur.fetchall()
    news = [dict(row) for row in news]
    print(news)

    cur.execute("SELECT COUNT(*) FROM PostTags")
    print(cur.fetchone()[0])

    return news