from flask import Flask
from flask import request
from flask import render_template

from BungieDatabase import BungieDatabase 

app = Flask(__name__)

db = None

@app.route('/')
def welcome():
    return render_template('welcome.html')
    
@app.route('/generate', methods=['GET'])
def get_stl():
    item = request.args.get('item')
    
    # Download the model data for this item
    model = db.getModel(item)
    
    # If the model is not null generate the stl file
    if model is not None:
        output = model.generate()
    else:
        output = 'Unable to find requested item'
    return render_template('output.html', output=output)
    
if __name__ == '__main__':
    # Create a Bungie Database object and connect to it
    db = BungieDatabase()
    db.connect()
    
    # Run Flask
    # app.debug = True
    app.run()
    
    # Close the database and exit
    db.close()
    exit()
