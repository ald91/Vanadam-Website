from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import EmailField, PasswordField, StringField, FileField, SelectMultipleField, SelectField, SubmitField, IntegerField, TextAreaField, widgets, BooleanField, FormField, HiddenField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, Optional

from .HaloData import infiniteCSR

#field contents
STANDARD_TIMEZONES = {
    "UTC": "UTC (Coordinated Universal Time)",

    # Europe
    "Europe/London": "London (UK)",
    "Europe/Paris": "Paris (Central Europe)",
    "Europe/Berlin": "Berlin (Central Europe)",
    "Europe/Madrid": "Madrid (Central Europe)",
    "Europe/Rome": "Rome (Central Europe)",
    "Europe/Athens": "Athens (Eastern Europe)",
    "Europe/Moscow": "Moscow",

    # Americas
    "America/New_York": "New York (Eastern Time)",
    "America/Chicago": "Chicago (Central Time)",
    "America/Denver": "Denver (Mountain Time)",
    "America/Los_Angeles": "Los Angeles (Pacific Time)",
    "America/Toronto": "Toronto",
    "America/Sao_Paulo": "São Paulo",
    "America/Mexico_City": "Mexico City",

    # Africa
    "Africa/Johannesburg": "Johannesburg",
    "Africa/Cairo": "Cairo",

    # Asia
    "Asia/Dubai": "Dubai",
    "Asia/Kolkata": "India (IST)",
    "Asia/Bangkok": "Bangkok",
    "Asia/Singapore": "Singapore",
    "Asia/Shanghai": "China",
    "Asia/Tokyo": "Tokyo",
    "Asia/Seoul": "Seoul",

    # Oceania
    "Australia/Sydney": "Sydney",
    "Australia/Melbourne": "Melbourne",
    "Australia/Perth": "Perth",
    "Pacific/Auckland": "Auckland"
}

SESSION_TYPES = ["Invidiual Vod Review", "Individual Shadow", "Team VoD Review", "Team Scrim Shadow", "Team Tournament Coach Slot", "Map Session"]   

# Class Construction
# ===================
# Construct search/filter, user validation and registration form classes
class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Length(min=3, max=16),
                               Regexp('^[A-Za-z][A-Za-z0-9_.]*$', )
                           ])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired(),
                                 Length(min=8, max=64),
                                 #TODO: Fix regexp, atm prevents logging in.
                                 #Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$')
                             ])
    submit = SubmitField('Login')

# Length and Regexp need checking
# Regexp seems properly buggered, needs a rework
class RegisterForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(message="Username is not Valid."),
                               Length(min=3, max=16, message="Usernames must be between 3 and 16 characters"),
                               # Regexp(r'^[A-Za-z][A-Za-a0-9_]*$', message="Usernames must contain letters, spaces or numbers only"),
                           ])

    email = EmailField('Email',
                       validators=[
                           DataRequired(message="Email is not Valid."),
                           Email()
                       ])

    password = PasswordField('Password',
                             validators=[
                                 DataRequired(),
                                 Length(min=8, max=64, message="Password must be between 8 and 64 characters."),
                                 # Regexp(
                                 #    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
                                 #    message="Password must contain uppercase, lowercase, number, and symbol."
                                 # )
                             ])

    password2 = PasswordField('Confirm Password',
                              validators=[
                                  DataRequired(),
                                  EqualTo('password', message="Passwords must match.")
                              ])

    submit = SubmitField('Register')

#for Admins setting and editing users
#uses same validation as Register form, could refactor for less code but meh WE CANT CHANGE USERPASSWORDS
class AdminUserForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(message="Username is not Valid."),
                               Length(min=3, max=16, message="Usernames must be between 3 and 16 characters"),
                               # Regexp(r'^[A-Za-z][A-Za-a0-9_]*$', message="Usernames must contain letters, spaces or numbers only"),
                           ])

    email = EmailField('Email',
                       validators=[
                           DataRequired(message="Email is not Valid."),
                           Email()
                       ])

    xboxname = StringField('Xbox GamerTag',
                           validators=[
                            DataRequired(message="Gamertag is required."),
                            Length(
                                min=3,
                                max=15,
                                message="Gamertag must be between 3 and 15 characters long."
                            ),
                            Regexp(
                                r"^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$",
                                message="Gamertag may only contain letters, numbers, and single spaces (no leading, trailing, or double spaces)."
                            ),
                        ])
    
    timezone = SelectField('enter your timezone', choices=list(STANDARD_TIMEZONES.keys()))
    arenarank = SelectField('enter your highest ranked area rank', choices=list(infiniteCSR.keys()))
    isAdmin = BooleanField('is this user an administrator (CAREFULL)')
    banned = BooleanField('is this user banned from posting in the forums?')
    submit = SubmitField('Modify User')



#users recover account using username and email
#uses same validation as login
class RecoveryForm(FlaskForm):
    username = StringField('Username')
    email = EmailField('Email')
    submit = SubmitField('Recovery')

#password change form
class PasswordResetForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    password2 = PasswordField('Password2')
    submit = SubmitField('submit')
    
#profile edit form for use in LFG and Forums later
class ProfileEditForm(FlaskForm):
    #only editable by Post request from /profile/<username>
    username = StringField('Username',
                        validators=[
                            DataRequired(message="Username is not Valid."),
                            Length(min=3, max=16, message="Usernames must be between 3 and 16 characters"),
                            # Regexp(r'^[A-Za-z][A-Za-a0-9_]*$', message="Usernames must contain letters, spaces or numbers only"),
                        ])
        
    email = EmailField('Email',
                    validators=[
                        DataRequired(message="Email is not Valid."),
                        Email()
                    ])
    
    xboxname = StringField('Xbox GamerTag',
                           validators=[DataRequired(message="Gamertag is required.")])
    
    timezone = SelectField('enter your timezone', choices=list(STANDARD_TIMEZONES.keys()))
    arenarank = SelectField('enter your highest ranked area rank', choices=list(infiniteCSR.keys()))
    submit = SubmitField('submit')

#I assume there will be some sort of issue with wtfforms datefield and sqlite as there is no date datatype but need
#to test this once we have hands on some data?
class SearchForm(FlaskForm):
    # Posts section
    date = DateField('Date', validators=[Optional()])
    date_selector = SelectField('Date Selector',choices=[('Before','Before'),('After','After'), ('On','On')])
    tags = StringField('Tags', validators=[Optional()])
    original_poster = StringField('Original Poster', validators=[Optional()])

    # Videos section
    vid_type = StringField('Video Type', validators=[Optional()])
    games = SelectMultipleField(
        'Game(s)',
        choices=[
            #('Halo: Combat Evolved', 'Halo: Combat Evolved'),
            #('Halo 2', 'Halo 2'),
            #('Halo 3', 'Halo 3'),
            #('Halo Wars', 'Halo Wars'),
            #('Halo 3: ODST', 'Halo 3: ODST'),
            #('Halo: Reach', 'Halo: Reach'),
            #('Halo 4', 'Halo 4'),
            #('Halo: Spartan Assault', 'Halo: Spartan Assault'),
            #('Halo: Spartan Strike', 'Halo: Spartan Strike'),
            #('Halo 5: Guardians', 'Halo 5: Guardians'),
            #('Halo Wars 2', 'Halo Wars 2'),
            ('Halo Infinite', 'Halo Infinite')
        ],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        validators=[Optional()]
    )

    maps = SelectMultipleField(
        'Maps',
        choices=[
           ('Aquarius', 'Aquarius'),
            ('Empyrean', 'Empyrean'),
            ('Forbidden', 'Forbidden'),
            ('Fortress', 'Fortress'),
            ('Lattice', 'Lattice'),
            ('Live Fire', 'Live Fire'),
            ('Origin', 'Origin'),
            ('Recharge', 'Recharge'),
            ('Serenity', 'Serenity'),
            ('Solitude', 'Solitude'),
            ('Streets', 'Streets'),
            ('Interference', 'Interference'),
            ('Starboard','Starboard'),
            ('Inquisitor','Inquisitor'),
            ('All Maps', 'All Maps')
        ],

        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        validators=[Optional()]
    )

    gamemode = SelectField(
        'Game Mode',
        choices=[
            ('', '-- Select a game mode --'),
            ('Capture the Flag', 'Capture the Flag'),
            ('Slayer', 'Slayer'),
            ('Oddball', 'Oddball'),
            #('Arena', 'Arena'),
            ('Strongholds', 'Strongholds'),
            #('Fiesta', 'Fiesta'),
            #('Juggernaut', 'Juggernaut'),
            ('King of the Hill', 'King of the Hill'),
            #('Stockpile', 'Stockpile'),
            ('Assault', 'Assault'),
            #('Domination', 'Domination')
        ],
        validators=[Optional()]
    )

    min_mmr = SelectField(
        'Min MMR',
        choices=[
            ('', '-- Select a minimum Rank --'),
            ('Bronze', 'Bronze'),
            ('Silver', 'Silver'),
            ('Gold', 'Gold'),
            ('Platinum', 'platinum'),
            ('Diamond', 'Diamond'),
            ('Onyx', 'Onyx'),
            ('EHL', 'EHL'),
            ('HCS', 'HCS'),

        ],
        validators=[Optional()]
    )

    max_mmr = SelectField(
        'Max MMR',
        choices=[
            ('', '-- Select a maximum Rank --'),
            ('Bronze', 'Bronze'),
            ('Silver', 'Silver'),
            ('Gold', 'Gold'),
            ('Platinum', 'platinum'),
            ('Diamond', 'Diamond'),
            ('Onyx', 'Onyx'),
            ('EHL', 'EHL'),
            ('HCS', 'HCS'),

        ],
        validators=[Optional()]
    )

    submit = SubmitField('Search')

class ArticleForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[
            DataRequired(message="Title is required."),
            Length(min=3, max=200, message="Title must be between 3 and 200 characters.")
        ]
    )
    
    description = TextAreaField(
        'Description',
        validators=[
            DataRequired(message="Content cannot be empty.")
        ]
    )


    content = TextAreaField(
        'Content',
        validators=[
            DataRequired(message="Content cannot be empty.")
        ]
    )

    tags = StringField(
        'Tags',
        validators=[
            Length(max=120, message="Tags cannot exceed 120 characters."),
            Regexp(
                r'^[A-Za-z0-9,\s\-]*$',
                message="Tags may contain letters, numbers, spaces, commas, and hyphens."
            )
        ]
    )
    image = FileField("Upload Image", validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

    hidden = BooleanField("Should this Article be visible", validators=[Optional()])

    submit = SubmitField('Save Article')

class ForumForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(min=3, max=256)]
    )
    content = TextAreaField(validators=[DataRequired()])

class CommentForm(FlaskForm):
    content = TextAreaField(
        "Comment",
        validators=[DataRequired(), Length(min=3, max=256)]
    )
    submit = SubmitField("Post Comment")

class ReportForm(FlaskForm):
    target_id = HiddenField()
    reason = TextAreaField(
        "Reason",
        validators=[DataRequired(), Length(min=3, max=256)]
    )
    submit = SubmitField("Report")

#fills coaching form days
class TimeSlotForm(FlaskForm):
    morning = BooleanField("Morning (08:00 - 11:59)")
    afternoon = BooleanField("Afternoon (12:00 - 16:59)")
    evening = BooleanField("Evening (17:00 - 21:59)")
    late = BooleanField("Late 22:00-24:00")

class CoachingForm(FlaskForm):
    crequestID = IntegerField("PK DO NOT EDIT")
    crequestTime = StringField("Time given by DB DO NOT EDIT")
    username = StringField("username")
    email = StringField("Email")
    timezone = SelectField("Enter Your Local Timezone", choices=STANDARD_TIMEZONES.keys())
    xboxname = StringField("Xbox Gamertag")
    coach = StringField("Select a coach (NYI for users)")
    arenarank = SelectField('Enter your current ranked area rank', choices=list(infiniteCSR.keys()))
    trackernetwork = StringField("URL for your profile (Trackernetwork / Leafapp / Haloquery / etc.)")
    sessiontype = SelectField("Select the session type", choices=list(SESSION_TYPES))
    agreeddate = StringField("Enter a valid date in format 0000-00-00 yyyy-mm-dd")
    agreedtime = StringField("Enter a valid time in format 00:00:00 24hr")
    monday = FormField(TimeSlotForm)
    tuesday = FormField(TimeSlotForm)
    wednesday = FormField(TimeSlotForm)
    thursday = FormField(TimeSlotForm)
    friday = FormField(TimeSlotForm)
    saturday = FormField(TimeSlotForm)
    sunday =  FormField(TimeSlotForm)
    details = TextAreaField("Enter any additional details here")
    invoiceID = StringField("Enter Invoice ID")
    paid = BooleanField("Paid by customer")
    delivered = BooleanField("Delivered by coach")
    submit = SubmitField("Send Request")

#youtube review request
from .HaloData import HALO_INFINITE_DATA
YTstatus = ["recieved", "queued", "recorded", "uploaded"]
possiblePlaylists = ["Ranked Arena", "Ranked Slayer", "Team Snipers", "Team Doubles"]
possibleMaps = list(HALO_INFINITE_DATA["Maps"])
possibleGameModes = [value for key, value in HALO_INFINITE_DATA["GameModes"].items() if key > 0]


class YouTubeReviewForm(FlaskForm):
    YTrequestID = IntegerField("PK DO NOT EDIT")
    YTrequestTime = StringField("Time given by DB DO NOT EDIT")
    username = StringField("username")
    xboxname = StringField("Xbox Gamertag", validators=[DataRequired(message="you must provide a valid gamertag")])
    arenarank = SelectField('Enter your current ranked area rank', choices=["", "- SELECT RANK -"] + list(infiniteCSR.keys()),  validators=[DataRequired(message="you must enter a valid arena rank")])
    videoURL = StringField('enter the url location of the video (xbox DVR / Youtube / Ondrive / Googledrive / etc.)', validators=[DataRequired(message="you must submit a valid URL")])
    trackernetwork = StringField("URL for The Match (Trackernetwork / Leafapp / Haloquery / etc.)")
    playlist = SelectField("Select the playlist for the match", choices=["", "- SELECT PLAYLIST -"] + possiblePlaylists , validators=[DataRequired(message="you must provide the playlist type for this submission")])
    matchmap = SelectField("Select the corresponding map the match is on", choices=["", "- SELECT A MAP -"] + possibleMaps,  validators=[DataRequired(message="you must provide the map type for this submission")])
    matchgamemode = SelectField("Select the corresponding game mode for the match", choices=["", "- SELECT GAMEMODE -"] + possibleGameModes , validators=[DataRequired(message="you must provide a game mode for this submission")])
    status = SelectField("current status of request", choices=YTstatus)
    youtubevideoID = StringField("admin enter URL for video here")
    submit = SubmitField("submit YouTube Review Request")
