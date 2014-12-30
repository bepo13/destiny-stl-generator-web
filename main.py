import json
from flask import Flask, request, render_template

from DestinyModel import DestinyModel 

app = Flask(__name__)

@app.route('/')
def welcome():
    # Load gear JSON file
    f = open("./gear/gear.json", 'r')
    gear = json.loads(f.read())
    f.close()
    
    for key in gear:
        print(gear[key]["name"])
        
    return render_template('welcome.html', gear=gear)
    
@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/generate', methods=['GET'])
def generate():
    item = request.args.get('item')
    key = item.replace('[',"").replace(']',"").lower()

    # Load gear JSON file
    f = open("./gear/gear.json", 'r')
    gear = json.loads(f.read())
    f.close()
    
    # Download the model data for this item
    try:
        model = DestinyModel(item, gear[key]["json"])
        output = model.generate()
    except:
        output = "Unable to find requested item: "+str(item)
        
    # Return the stl output or response
    return render_template('output.html', output=output)
    
if __name__ == '__main__':
    # Run Flask
    # app.debug = True
    app.run()
