import os
import json
from flask import Flask, request, render_template, send_file

from DestinyModel import DestinyModel 

app = Flask(__name__)

outputPath = "stl/"

@app.route('/')
def welcome():
    # Load gear JSON file
    f = open("./gear/gear.json", 'r')
    gear = json.loads(f.read())
    f.close()
        
    return render_template('welcome.html', gear=gear)
    
@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/generate', methods=['GET'])
def generate():
    item = request.args.get('item')
    key = item.replace('[',"").replace(']',"").replace('\'',"").lower()

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
    else:
        try:
            # Create temp directory
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
                
            # Write temp file if it does not already exist
            filePath = outputPath+key+".stl"
            if not os.path.exists(filePath):
                with open(filePath, 'w') as fo:
                    fo.write(output)
                    fo.close()
            print("Wrote output file "+filePath)
        except:
            print("Unable to create file "+filePath)
        
    # Return the stl output or response
    return render_template('output.html', output=output)

@app.route('/stl/<path:filename>')
def send_tmp_file(filename):
    try:
        if ".." in filename:
           return "Error retrieving file"
        else:
            path = outputPath+filename
            print("Sending",path)
            return send_file(path)
    except:
       return "Error retrieving file"
        
if __name__ == '__main__':
    # Run Flask
    # app.debug = True
    app.run()
