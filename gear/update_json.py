import os
import io
import re
import json
import struct
import urllib.request
import zipfile
import sqlite3

bungieUrlPrefix = "http://www.bungie.net"
destinyManifestUrl = "http://www.bungie.net/platform/Destiny/Manifest/"
headers = {"X-API-Key": "37929154a3fb499fa908cf2a2d75c6a8"}
jsonFile = "./gear.json"

def main():
    # Open the Destiny manifest from bungie.net and load it as json
    print("Downloading gear database from bungie.net...")
    request = urllib.request.Request(destinyManifestUrl, headers=headers)
    response = urllib.request.urlopen(request)
    manifest = json.loads(response.read().decode())
    
    # Read the path for the gear database file and open it
    path = bungieUrlPrefix+manifest["Response"]["mobileGearAssetDataBases"][1]["path"]
    request = urllib.request.Request(path, headers=headers)
    response = urllib.request.urlopen(request)

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
        itemJson = json.loads(row[1])
        try:
            itemUrl = destinyManifestUrl+"inventoryItem/"+str(itemId)
            request = urllib.request.Request(itemUrl, headers=headers)
            response = urllib.request.urlopen(request)
            itemManifest = json.loads(response.read().decode())
            itemName = itemManifest["Response"]["data"]["inventoryItem"]["itemName"].replace('"',"").rstrip()
            itemTypeName = itemManifest["Response"]["data"]["inventoryItem"]["itemTypeName"].replace('"',"").rstrip()
            itemTierName = itemManifest["Response"]["data"]["inventoryItem"]["tierTypeName"].replace('"',"").rstrip()
            
            if ("Armor Shader" in itemTypeName) or ("Restore Defaults" in itemTypeName):
                # Skip shaders
                print("Ignoring shader with id",itemId,"...")
                continue
            elif "###Missing String" in itemName:
                # Missing item name, skip
                print("Skipping item with missing item name, id",itemId,"...")
                continue
            elif len(itemJson["content"]) == 0:
                # Item has no content, skip
                print("Skipping item with missing content, id",itemId,"...")
                continue
            elif "geometry" not in itemJson["content"][0]:
                # Item has no geometry, skip
                print("Skipping item with missing geometry, id",itemId,"...")
                continue
            else:
                # Create separate entries for male and female items
                if ("male_index_set" in itemJson["content"][0]) or ("female_index_set" in itemJson["content"][0]):
                    # Check for male index set
                    if "male_index_set" in itemJson["content"][0]:
                        # Create complete item name and dictionary key
                        itemCompleteName = itemName+" [Male] ["+itemTypeName+"] ["+itemTierName+"] ["+str(itemId)+"]"
                        key = re.sub(r'[^a-zA-Z0-9 ]', '', itemCompleteName).lower()
                        
                        # Add the item to the gear JSON
                        print("Adding "+itemCompleteName)
                        print("  key: "+key)
                        print("  url: "+itemUrl)
                        gear[key] = {"id": itemId, "name": itemCompleteName, "json": itemJson}
                    
                    # Check for female index set
                    if "female_index_set" in itemJson["content"][0]:
                        # Create complete item name and dictionary key
                        itemCompleteName = itemName+" [Female] ["+itemTypeName+"] ["+itemTierName+"] ["+str(itemId)+"]"
                        key = re.sub(r'[^a-zA-Z0-9 ]', '', itemCompleteName).lower()
                        
                        # Add the item to the gear JSON
                        print("Adding "+itemCompleteName)
                        print("  key: "+key)
                        print("  url: "+itemUrl)
                        gear[key] = {"id": itemId, "name": itemCompleteName, "json": itemJson}
                else:
                    # Create complete item name and dictionary key
                    itemCompleteName = itemName+" ["+itemTypeName+"] ["+itemTierName+"] ["+str(itemId)+"]"
                    key = re.sub(r'[^a-zA-Z0-9 ]', '', itemCompleteName).lower()
                    
                    # Add the item to the gear JSON
                    print("Adding "+itemCompleteName)
                    print("  key: "+key)
                    print("  url: "+itemUrl)
                    gear[key] = {"id": itemId, "name": itemCompleteName, "json": itemJson}
        except Exception as e:
            # Skip this entry
            print(str(e))
            print("Skipping item id",itemId,"...")
            continue
    
    conn.close()
    print("Done updating the gear dictionary...")

    # Write the dictionary to JSON file
    try:
        if os.path.isfile(jsonFile):
            os.remove(jsonFile)
            print("Deleted old gear JSON file...")
        fo = open(jsonFile, 'w')
        fo.write(json.dumps(gear))
        fo.close()
        print("Successfully wrote JSON file...")
    except:
        print("Error writing the JSON file, exiting")
        os.remove(bungieDbFile)
        exit()
        
    print("Cleaning up temp files...")
    os.remove(bungieDbFile)
    
    print("Done")
    exit()

if __name__ == '__main__':
    main()
