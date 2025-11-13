from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SelectMultipleField, SelectField, SubmitField, IntegerField, widgets
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, Optional

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
                                 Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$')
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
    #only editable by PATCH request from /profile/<username>
    username = StringField()
    gamertag = StringField()
    # current_mmr = 

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