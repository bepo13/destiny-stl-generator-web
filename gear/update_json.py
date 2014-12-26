import io
import json
import struct
import os
import urllib.request
import zipfile
import sqlite3

bungieUrlPrefix = "http://www.bungie.net"
destinyManifestUrl = "http://www.bungie.net/platform/Destiny/Manifest/"
jsonFile = "./gear.json"

def main():
    if os.path.isfile(jsonFile):
        print("Deleting old gear JSON file...")
        os.remove(jsonFile)
        
    # Open the Destiny manifest from bungie.net and load it as json
    print("Downloading gear database from bungie.net...")
    response = urllib.request.urlopen(destinyManifestUrl)
    manifest = json.loads(response.read().decode())
    
    # Read the path for the gear database file and open it
    path = bungieUrlPrefix+manifest["Response"]["mobileGearAssetDataBases"][1]["path"]
    response = urllib.request.urlopen(path)

    # Gunzip the database file
    gearZip = zipfile.ZipFile(io.BytesIO(response.read()))
    zipNameList = gearZip.namelist()
    for filename in zipNameList:
        if "asset_sql_content" in filename:
            gearZip.extract(filename)
            bungieDbFile = filename
    
    # Create gear dictionary
    print("Creating new gear dictionary...")
    gear = {}
    
    print("Updating the gear database...")
    print("This will take a few minutes...")
    
    # Open the database and get a cursor object
    conn = sqlite3.connect(bungieDbFile)
    c = conn.cursor()
    
    # Get the names for all items
    c.execute("SELECT id, json FROM DestinyGearAssetsDefinition")
    for row in c:
        itemId = struct.unpack('L', struct.pack('l', row[0]))[0]
        itemJson = row[1]
        try:
            response = urllib.request.urlopen(destinyManifestUrl+"inventoryItem/"+str(itemId))
            itemManifest = json.loads(response.read().decode())
            itemName = itemManifest["Response"]["data"]["inventoryItem"]["itemName"].replace('"',"").rstrip().lower()
            print("Adding "+itemName+" from: "+destinyManifestUrl+"inventoryItem/"+str(itemId))
            gear[itemName] = itemJson
        except:
            # Skip this entry
            print("Skipping item id",itemId,"...")
            continue
    
    conn.close()
    print("Done updating the gear dictionary...")

    # Write the dictionary to JSON file
    try:
        fo = open(jsonFile, 'w')
        fo.write(json.dumps(gear))
        fo.close()
        print("Successfully wrote JSON file...")
    except:
        print("Error writing the JSON file, exiting")
        exit()
        
    print("Cleaning up temp files...")
    os.remove(bungieDbFile)
    
    print("Done")
    exit()

if __name__ == '__main__':
    main()
