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
        
        if "[Male]" in name:
            # Parse all the geometry indices for male items and parse the geometries
            for geometryIndex in self.json["content"][0]["male_index_set"]["geometry"]:
                geometryFile = self.json["content"][0]["geometry"][geometryIndex]
                path = bungieUrlPrefix+bungieGeometryPrefix+geometryFile
                print("Geometry file: "+path)
                response = urllib.request.urlopen(path)
                data = DataParse.DataParse(response.read())
                self.geometry.append(DestinyGeometry.parse(data))
        elif "[Female]" in name:
            # Parse all the geometry indices for female items and parse the geometries
            for geometryIndex in self.json["content"][0]["female_index_set"]["geometry"]:
                geometryFile = self.json["content"][0]["geometry"][geometryIndex]
                path = bungieUrlPrefix+bungieGeometryPrefix+geometryFile
                print("Geometry file: "+path)
                response = urllib.request.urlopen(path)
                data = DataParse.DataParse(response.read())
                self.geometry.append(DestinyGeometry.parse(data))
        else:
            # Get the geometry file names from the json and parse the geometries
            for geometryFile in self.json["content"][0]["geometry"]:
                path = bungieUrlPrefix+bungieGeometryPrefix+geometryFile
                print("Geometry file: "+path)
                response = urllib.request.urlopen(path)
                data = DataParse.DataParse(response.read())
                self.geometry.append(DestinyGeometry.parse(data))
        
        return
    
    def generate(self, fileStl, fileZip):        
        #Open string file
        fo = io.StringIO()
        
        # Write name header
        fo.write("solid\n")
         
        # Generate stl data for each geometry
        for geometry in self.geometry:
            print("test")
            status = geometry.generate(fo)
            if status == False:
                # Something went wrong, cleanup the file and return
                fo.close()
                return "Unable to parse request item geometry"
        
        # Retrieve string contents and close string file
        contents = fo.getvalue()
        fo.close()
        
        # Write output file
        with open(fileStl, 'w') as fo:
            fo.write(contents)
            fo.close()
        print("Wrote output file "+fileStl)
            
        return contents
    