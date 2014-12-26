import json
from flask import Flask
from flask import request
from flask import render_template

from DestinyModel import DestinyModel 

app = Flask(__name__)

gear = None
gearFile = "./gear/gear.js"

@app.route('/')
def welcome():
    return render_template('welcome.html')
    
@app.route('/generate', methods=['GET'])
def generate():
    item = request.args.get('item')
    
    # Download the model data for this item
    try:
        model = DestinyModel(item, gear[item.lower()])
        output = model.generate()
    except:
        output = 'Unable to find requested item'
        
    # Return the stl output or response
    return render_template('output.html', output=output)
    
if __name__ == '__main__':
    # Load gear JSON file
    fi = open(gearFile, 'r')
    gear = json.loads(fi.read())
    gear = {k.lower():v for k,v in gear.items()}
    fi.close()
    
    # Run Flask
    # app.debug = True
    app.run()
