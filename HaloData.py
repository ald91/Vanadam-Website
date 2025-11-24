

#easy modification of website data without pissing about with back end?

#on boot from JSON
def Build_Halo_Data(form, credentials):
    pass

# modify JSON (CLASS???)
def Modify_Halo_Data(form, credentials):
    pass


#Data stored by game
#can edit using admin panel

GAME_MODES = {
    0 : "Not in rotation",
    1 : "Strongholds",
    2 : "KOTH",
    3 : "CTF",
    4 : "Oddball",
    5 : "Slayer",
    6 : "Assault"
}

HALO_3_DATA = {
    "Game" : "Halo 3",
    "Maps" : { 
        "placeholder": {
            "name": None,
            "description": None,
            "ranked arena" : None,
            "MM modes": None,
        },

    }
}

HALO_INFINITE_DATA = {
    "Game" : "Halo:Infinite",
    "Maps" :  {
        "Aquarius": {
            "name": "Aquarius",
            "description": "Aquarius Terraforming Solutions: Industry leader in returning life to barren worlds.",
            "ranked arena" : True,
            "MM modes": "3 5 6",
            "HCS modes": "3 5 6",
            "EHL modes": "3 5 6"
        },
        
        "Argyle": {
            "name": "Argyle",
            "description": "An incredible feat of engineering.",
            "ranked arena" : False,
            "MM modes": "0",
            "HCS modes": "0",
            "EHL modes": "0"
        },
        
        "Bazaar": {
            "name": "Bazaar",
            "description": "Dusty streets and double doors.",
            "ranked arena" : False,
            "MM modes": "0",
            "HCS modes": "0",
            "EHL modes": "0"
        },

        "Empyrean": {
            "name": "Empyrean",
            "description": "Sleepless nights, timeless fights.",
            "ranked arena" : True,
            "MM modes": "5",
            "HCS modes": " 0 ",
            "EHL modes": " 0 "
        },

        "Forbidden": {
            "name": "Forbidden",
            "description": "These halls hide history of both triumph and terror.",
            "ranked arena" : True,
            "MM modes": "3",
            "HCS modes": "3",
            "EHL modes": "3"
        },

        "Fortress": {
            "name": "Fortress",
            "description": "Battles of long ago echo throughout the valley.",
            "ranked arena" : True,
            "MM modes": " 3 6 ",
            "HCS modes": "3 6 ",
            "EHL modes": "3 6"
            
        },

        "Inquisitor" : {
            "name": "Inquisitor",
            "description" : "Don't let its luxury fool you the Pious Inquisitor is one of the fastest ships in the Covenant fleet.",
            "ranked arena" : False,
            "MM modes": " 0",
            "HCS modes": " 0 ",
            "EHL modes": " 0 "
        },

        "Interference": {
            "name" : "Interference",
            "description": "Reimagination of the Halo 5's map The Rig with a snowy theme. Upscaled to accommodate Infinite's mechanics",
            "ranked arena" : False,
            "MM modes": " 0 ",
            "HCS modes": " 0 ",
            "EHL modes": " 0 "
        },

        "Live fire": {
            "name": "Live Fire",
            "description": "Instructors at the Avery J. Johnson Academy of Military Science ensure their Spartans are prepared for any challenge.",
            "ranked arena" : True,
            "MM modes": "1 2 4 5",
            "HCS modes": "1 2 4 5",
            "EHL modes": "1 2 4 5"
        },

        "Lattice": {
            "name": "Lattice",
            "description": "This abandoned hydroelectric facility holds secrets once buried under the ice.",
            "ranked arena" : True,
            "MM modes": "1 2 4 5",
            "HCS modes": "1 2 4 5",
            "EHL modes" : "1 2 4 5"
        },        

        "Origin": {
            "name": "Origin",
            "description": "Forerunner Warrior-Servants tested themselves in this arena before facing the Flood. Remake of Halo 5 Coliseum. Plays 4v4 CTF, Slayer, Strongholds, Oddball, King of the Hill, and Free For All",
            "ranked arena" : True,
            "MM modes": "3 5",
            "HCS modes": "3 5",
            "EHL modes": "3 5"
        },

        "Recharge": {
            "name": "Recharge",
            "description": "Power still courses through the walls of this neglected Axys facility.",
            "ranked arena" : True,
            "MM modes": "1 2 4 5",
            "HCS modes": "1 2 4 5",
            "EHL modes": "1 2 4 5"
        },

        "Starboard": {
            "name" : "Starboard",
            "description": "General quarters, general quarters. All hands man your battle stations.",
            "ranked arena" : False,
            "MM modes": " 0",
            "HCS modes": " 0 ",
            "EHL modes": " 0 "
        },
     
        "Serenity": {
            "name": "Serenity",
            "description": "Amidst ancient ruins, tranquil waters flow through a symmetrical landscape. This Sanctuary, once sacred, now echoes with battle cries",
            "ranked arena" : True,
            "MM modes": " 3 6 ",
            "HCS modes": " 0 ",
            "EHL modes": " 0 "
        },

        "Solitude": {
            "name": "Solitude",
            "description": "Not all life finds a way.",
            "ranked arena" : True,
            "MM modes": " 2 5 ",
            "HCS modes": " 5 ",
            "EHL modes": " 2 5 "
        },

        "Streets": {
            "name": "Streets",
            "description": "The tranquility of this Mombasa back alley is pierced by the sound of heavy gunfire.",
            "ranked arena" : True,
            "MM modes": " 4 5 ",
            "HCS modes": " 5 ",
            "EHL modes": " 4 5 "
        },

        "Vacancy" : {
            "name" : "Vacancy",
            "description" : "You can check out any time you like, but you can never leave.",
            "ranked arena" : True,
            "MM modes" : " 5 ",
            "HCS modes": " 0 ",
            "EHL modes": " 0 "
        }
    }
}
