import os
import re
import json
from flask import Flask, request, render_template, send_file

from DestinyModel import DestinyModel 

app = Flask(__name__, static_folder='assets')

outputPath = "stl/"

@app.route('/')
def welcome():
    # Load and format D1 gear data
    f = open("./gear/gear_d1.json", 'r')
    gear_d1 = json.loads(f.read())
    data_d1 = []
    for k, v in gear_d1.items():
        data_d1.append({"text": v["name"], "id": v["name"]})
    f.close()

    # Load and format D2 gear data
    f = open("./gear/gear_d2.json", 'r')
    gear_d2 = json.loads(f.read())
    data_d2 = []
    for k, v in gear_d2.items():
        data_d2.append({"text": v["name"], "id": v["name"]})
    f.close()
        
    return render_template('home.html', data_d1=data_d1, data_d2=data_d2)
    
@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/download', methods=['GET'])
def download():
    # Parse the arguments for item name and generate the key
    item = request.args.get('item')
    key = re.sub(r'[^a-zA-Z0-9 ]', '', item).lower()
    
    # Create file names
    fileName = key.replace(" ","_")
    fileNameStl = fileName+".stl"
    filePathStl = outputPath+fileNameStl
    fileNameZip = fileName+".zip"
    filePathZip = outputPath+fileNameZip
    
    # Create output directory
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    
    # Check if file has already been created
    if os.path.exists(filePathStl):
        print("Using existing file "+fileNameStl)
    else:
        # Load gear JSON files
        f = open("./gear/gear_d1.json", 'r')
        gear_d1 = json.loads(f.read())
        f.close()
        f = open("./gear/gear_d2.json", 'r')
        gear_d2 = json.loads(f.read())
        f.close()
        
        # Download the model data for this item
        try:
            # Download the model geometries
            if key in gear_d1:
                print("Loading D1 model with key "+key+"...")
                model = DestinyModel(item, gear_d1[key]["json"], 0)
            elif key in gear_d2:
                print("Loading D2 model with key "+key+"...")
                model = DestinyModel(item, gear_d2[key]["json"], 1)
            
            # Generate the output
            print("Generating output...")
            model.generate(filePathStl, filePathZip)
        except:
            output = "Unable to generate files for item: "+str(item)
            return render_template('output.html', output=output)
            # error page
            
    # Return the file download page
    return render_template('download.html', item=item, fileNameStl=fileNameStl, filePathStl=filePathStl, fileNameZip=fileNameZip, filePathZip=filePathZip)

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
