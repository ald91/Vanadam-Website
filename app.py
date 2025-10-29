# This code imports the Flask library and some functions from it.
from flask import Flask, render_template
from HaloData import HI_MAPS

# Create a Flask application instance
app = Flask(__name__)

# Routes
#===================
# These define which template is loaded, or action is taken, depending on the URL requested
#===================
# Home Page
@app.route('/')
def index():
    return render_template('home.html', title="Vanadam Halo")

@app.route('/mapPage/<mapID>', methods=['GET'])
def mapPage(mapID):
    print(f'got request for: {mapID}')
    mapID = str(mapID).capitalize()
    map_data = HI_MAPS.get(mapID)
    if not map_data:
        return render_template('404.html')
    
    print(map_data)
    return render_template('map.html', map=map_data)

@app.route('/login', methods=['GET'])
def login():
    pass

@app.route('/logout', methods=[])
def logout():
    pass

@app.route('/register', methods=['GET', 'POST'])
def register():
    pass

@app.route('/report', methods=['POST'])
def report():
    pass

# Run application
#=========================================================
# This code executes when the script is run directly.
if __name__ == '__main__':
    print("Starting Flask application...")
    print("Open Your Application in Your Browser: http://localhost:81")
    # The app will run on port 81, accessible from any local IP address
    app.run(host='0.0.0.0', port=81)
