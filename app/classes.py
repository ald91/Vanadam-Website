#NOTE: Ryan, i dont intend to implement these until after EFSSD. dont worry :)

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

@dataclass
class CoachingRequest:

    """ a coaching object that contains information from COACHING table and the associated JSON"""
    
    crequestID:int 
    userID:int       
    username:str     
    email:str        
    xboxname:str     
    arenarank:str    
    sessiontype:str  
    coach:str        
    timezone:str     
    agreedtime:str   
    delivered:bool   
    paid:bool        
    invoiceID:str    
    json:str
    timeslots: list[list[bool,bool,bool,bool]]
    
        