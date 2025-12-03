from db import get_database

#TODO: function fetch sidebar
#TODO: get this done

def fetchSideBar(results):
    
    """fetches records from DB for the home page right side bar area"""

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



def fetchNewsBar(results):

    """fetches records from DB for the home page bottom area"""

    db = get_database()
    cur = db.cursor()

    newstags = ('Discussion', 'Map Guide', 'News')
    params = newstags + newstags, (results,)

    newsquery = """
    SELECT *
    FROM (
        SELECT 'Video' AS type, v.postID, v.title, v.thumbnailsmax, v.description, p.date
        FROM Videos v
        JOIN Posts p on v.postID = p.postID
        JOIN PostTags pt ON v.postID = pt.postID
        WHERE pt.tagName IN (?, ?, ?)

        UNION ALL

        SELECT 'Article' AS type, a.postID, a.title, a.image_filename, a.description, p.date
        FROM Articles a
        JOIN Posts p on a.postID = p.postID
        JOIN PostTags pt ON a.postID = pt.postID
        WHERE pt.tagName IN (?, ?, ?)
    )
    ORDER BY date DESC
    LIMIT ?;
    """

    cur.execute(newsquery, params)
    news = cur.fetchall()
    news = [dict(row) for row in news]

    return news