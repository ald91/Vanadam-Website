from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SelectMultipleField, SelectField, SubmitField, IntegerField, widgets
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, Optional

# Class Construction
# ===================
# Construct user validation and registration form classes
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


class SearchForm(FlaskForm):
    # Posts section
    date = StringField('Date', validators=[Optional()])
    tags = StringField('Tags', validators=[Optional()])
    original_poster = StringField('Original Poster', validators=[Optional()])

    # Videos section
    vid_type = StringField('Video Type', validators=[Optional()])

    # Games multi-select (checkboxes)
    games = SelectMultipleField(
        'Game(s)',
        choices=[
            ('Halo: Combat Evolved', 'Halo: Combat Evolved (2001)'),
            ('Halo 2', 'Halo 2 (2004)'),
            ('Halo 3', 'Halo 3 (2007)'),
            ('Halo Wars', 'Halo Wars (2009)'),
            ('Halo 3: ODST', 'Halo 3: ODST (2009)'),
            ('Halo: Reach', 'Halo: Reach (2010)'),
            ('Halo 4', 'Halo 4 (2012)'),
            ('Halo: Spartan Assault', 'Halo: Spartan Assault (2013)'),
            ('Halo: Spartan Strike', 'Halo: Spartan Strike (2015)'),
            ('Halo 5: Guardians', 'Halo 5: Guardians (2015)'),
            ('Halo Wars 2', 'Halo Wars 2 (2017)'),
            ('Halo Infinite', 'Halo Infinite (2021)')
        ],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        validators=[Optional()]
    )

    # Maps multi-select
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

    # Game mode select
    gamemode = SelectField(
        'Game Mode',
        choices=[
            ('', '-- Select a game mode --'),
            ('Capture the Flag', 'Capture the Flag'),
            ('Slayer', 'Slayer'),
            ('Oddball', 'Oddball'),
            ('Arena', 'Arena'),
            ('Strongholds', 'Strongholds'),
            ('Fiesta', 'Fiesta'),
            ('Juggernaut', 'Juggernaut'),
            ('King of the Hill', 'King of the Hill'),
            ('Stockpile', 'Stockpile'),
            ('Assault', 'Assault'),
            ('Domination', 'Domination')
        ],
        validators=[Optional()]
    )

    min_mmr = IntegerField('Min MMR', validators=[Optional()])
    max_mmr = IntegerField('Max MMR', validators=[Optional()])

    submit = SubmitField('Search')