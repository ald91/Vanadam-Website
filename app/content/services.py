from ..data.db import get_database
from flask import request

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

def process_search():
    """Receives arguments from content.routes.search(), called in content.routes.results"""
    db = get_database()
    cur = db.cursor()

    # Pull params from URL
    date = request.args.get("date")
    date_selector = request.args.get("date_selector")
    tags = request.args.get("tags")
    vid_type = request.args.get("vid_type")
    gamemode = request.args.get("gamemode")
    min_csr = request.args.get("min_csr")
    max_csr = request.args.get("max_csr")
    selected_maps = request.args.getlist("maps")

    # =====================
    # Base query
    # =====================
    query = """
            SELECT Posts.postID, \
                   Posts.date, \
                   Videos.vidID, \
                   Videos.title   AS video_title, \
                   Videos.csr, \
                   Videos.gamemap, \
                   Videos.gamemode, \
                   Videos.videotype, \
                   Articles.articleID, \
                   Articles.title AS article_title, \
                   Articles.description, \
                   Articles.image_filename
            FROM Posts
                     LEFT JOIN Videos ON Videos.postID = Posts.postID
                     LEFT JOIN Articles ON Articles.postID = Posts.postID \
            """

    conditions = []
    params = []

    # =====================
    # Filters
    # =====================
    if date:
        if date_selector == "On":
            conditions.append("date(Posts.date) = date(?)")
        elif date_selector == "Before":
            conditions.append("date(Posts.date) < date(?)")
        elif date_selector == "After":
            conditions.append("date(Posts.date) > date(?)")
        params.append(date)

    if vid_type:
        conditions.append("Videos.videotype = ?")
        params.append(vid_type)

    if gamemode:
        conditions.append("Videos.gamemode = ?")
        params.append(gamemode)

    if selected_maps:
        placeholders = ",".join("?" for _ in selected_maps)
        conditions.append(f"Videos.gamemap IN ({placeholders})")
        params.extend(selected_maps)

    if min_csr:
        conditions.append("Videos.csr >= ?")
        params.append(min_csr)

    if max_csr:
        conditions.append("Videos.csr <= ?")
        params.append(max_csr)

    if tags:
        query += """
            JOIN PostTags ON PostTags.postID = Posts.postID
            JOIN Tags ON Tags.tagName = PostTags.tagName
            """
        conditions.append("Tags.tagName = ?")
        params.append(tags)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    results = cur.execute(query, params)
    results = [dict(row) for row in results]

    return results