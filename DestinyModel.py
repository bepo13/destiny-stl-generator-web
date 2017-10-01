import io
import os
import json
import urllib
import zipfile

import DataParse
import DestinyGeometry

bungieUrlPrefix = "http://www.bungie.net"
bungieGeometryPrefix = ["/common/destiny_content/geometry/platform/mobile/geometry/",
                        "/common/destiny2_content/geometry/platform/mobile/geometry/"]
headers = {"X-API-Key": "37929154a3fb499fa908cf2a2d75c6a8"}

class DestinyModel(object):
    def __init__(self, name, jsonData, game):
        self.geometry = []
        self.name = name
        
        # Load the json file
        self.json = jsonData
        
        print("Processing geometries...")
        # print(json.dumps(self.json, indent=4, sort_keys=True))
        
        if "[Male]" in name:
            # Parse all the geometry indices for male items and parse the geometries
            for geometryIndex in self.json["content"][0]["male_index_set"]["geometry"]:
                geometryFile = self.json["content"][0]["geometry"][geometryIndex]
                path = bungieUrlPrefix+bungieGeometryPrefix[game]+geometryFile
                print("Geometry file: "+path)
                request = urllib.request.Request(path, headers=headers)
                response = urllib.request.urlopen(request)
                data = DataParse.DataParse(response.read())
                self.geometry.append(DestinyGeometry.parse(data))
        elif "[Female]" in name:
            # Parse all the geometry indices for female items and parse the geometries
            for geometryIndex in self.json["content"][0]["female_index_set"]["geometry"]:
                geometryFile = self.json["content"][0]["geometry"][geometryIndex]
                path = bungieUrlPrefix+bungieGeometryPrefix[game]+geometryFile
                print("Geometry file: "+path)
                request = urllib.request.Request(path, headers=headers)
                response = urllib.request.urlopen(request)
                data = DataParse.DataParse(response.read())
                self.geometry.append(DestinyGeometry.parse(data))
        else:
            # Get the geometry file names from the json and parse the geometries
            for geometryFile in self.json["content"][0]["geometry"]:
                path = bungieUrlPrefix+bungieGeometryPrefix[game]+geometryFile
                print("Geometry file: "+path)
                request = urllib.request.Request(path, headers=headers)
                response = urllib.request.urlopen(request)
                data = DataParse.DataParse(response.read())
                self.geometry.append(DestinyGeometry.parse(data))
        
        print("Done processing geometries...")
        return
    
    def generate(self, filePathStl, filePathZip):        
        # Open stl and zip files
        fStl = open(filePathStl, 'w')
        fZip = zipfile.ZipFile(filePathZip, 'w', zipfile.ZIP_DEFLATED)
         
        # Generate stl data for each geometry
        for geometry in self.geometry:
            status = geometry.generate(fStl, fZip)
            if status == False:
                # Something went wrong, cleanup the file and return
                fo.close()
                return "Unable to parse request item geometry"
            
        print("Wrote output file "+filePathStl)
        
        # Close stl and zip files
        fStl.close()
        fZip.close()
            
        return
    