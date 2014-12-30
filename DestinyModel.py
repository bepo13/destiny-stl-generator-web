import io
import os
import json
import urllib

import DataParse
import DestinyGeometry

bungieUrlPrefix = "http://www.bungie.net"
bungieGeometryPrefix = "/common/destiny_content/geometry/platform/mobile/geometry/"

class DestinyModel(object):
    def __init__(self, name, jsonData):
        self.geometry = []
        self.name = name
        
        # Load the json file
        self.json = jsonData
        
        print("Processing geometries...")
            
        # Get the geometry file names from the json and parse the geometries
        for geometryFile in self.json["content"][0]["geometry"]:
            path = bungieUrlPrefix+bungieGeometryPrefix+geometryFile
            print("Geometry file: "+path)
            response = urllib.request.urlopen(path)
            data = DataParse.DataParse(response.read())
            self.geometry.append(DestinyGeometry.parse(data))
        
        return
    
    def generate(self):
        #Open string file
        fo = io.StringIO()
        
        # Write name header
        fo.write("solid\n")
         
        # Generate stl data for each geometry
        for geometry in self.geometry:
            status = geometry.generate(fo)
            if status == False:
                # Something went wrong, cleanup the file and return
                fo.close()
                return "Unable to parse request item geometry"
        
        # Retrieve string contents and close string file
        contents = fo.getvalue()
        fo.close()
            
        return contents
    