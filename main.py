import json
from flask import Flask, request, render_template

from DestinyModel import DestinyModel 

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('welcome.html')
    
@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/generate', methods=['GET'])
def generate():
    item = request.args.get('item')

    # Load gear JSON file
    f = open("./gear/gear.json", 'r')
    gear = json.loads(f.read())
    f.close()
    
    # Download the model data for this item
    try:
        model = DestinyModel(item, gear[item.lower()])
        output = model.generate()
    except:
        output = "Unable to find requested item: "+item
        
    # Return the stl output or response
    return render_template('output.html', output=output)
    
if __name__ == '__main__':
    # Run Flask
    # app.debug = True
    app.run()
