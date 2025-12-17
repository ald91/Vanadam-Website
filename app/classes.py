from dataclasses import dataclass

@dataclass
class Article:
    
    """ a Article object that contains information on the files associated with the Article
    content files are A{ArticleID}.JSON and IMG files are A{ArticleID}.jpeg
    
    PostTags are foreign data extracted from a linking table"""
    
    articleID: int
    postID: int
    title: str
    description: str
    json_filename: str
    image_filename: str
    hidden: bool

@dataclass
class Video:

    """ a video object that contains information on the video db information based on YT API_V3 Pulls"""

    vidID: int
    postID: int
    PostTags: list[str]
    title: str
    duration: int
    published: str
    description: str
    thumbnailsdefault: str
    thumbnailshigh: str
    thumbnailsmax: str
    kind: str
    channelid: str
    csr: int
    gamemap: str
    gamemode: str
    videotype: str
    etag: str