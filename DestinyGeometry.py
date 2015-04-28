import io
import json
import struct
from DataParse import VertexParse

offsetConst = 0.0
scaleConst = 1000.0

class EmptyObject(object):
    pass

class DestinyGeometry:
    def __init__(self, data):
        # Read header
        self.extension = data.readString(4)
        data.readInt32()                #not sure what this number is
        self.headerSize = data.readInt32()
        self.fileCount = data.readInt32()
        self.name = data.readString(256)
        self.files = []
        
        try:
            # Parse header for file data
            i = self.fileCount
            while i > 0:
                file = EmptyObject()
                file.name = data.readString(256)
                file.startAddr = data.readInt64()
                file.length = data.readInt64()
                
                # Flag the index of the render file
                if "render_metadata.js" in file.name:
                    jsonIndex = len(self.files)
                
                self.files.append(file)
                i -= 1
        except:
            print("Error parsing file header!")
        
        # Read in files
        try:
            i = 0
            while i < self.fileCount:
                data.seek(self.files[i].startAddr)
                self.files[i].data = data.read(self.files[i].length)
                i += 1
        except:
            print("Error reading in files!")
            
        try:
            # Load the meshes from the render_metadata.js file
            self.meshes = json.loads(self.files[jsonIndex].data.decode())["render_model"]["render_meshes"]
        except:
            print("Error loading meshes from render_metadata.js")
            
        return
    
    def get(self, filename):
        for i in range(self.fileCount):
            if filename == self.files[i].name:
                return self.files[i]
        print("Unable to retrieve geometry file",filename,", please file an issue for this item...")
        return
        
    def generate(self, fStl, fZip):
        # Parse each mesh in the geometry
        for meshCount, mesh in enumerate(self.meshes):
            # Parse the normal and positional vertex buffers (ignore everything else for now)
            positions = []
            normals = []
            defVB = mesh["stage_part_vertex_stream_layout_definitions"][0]["formats"]
            for i, vB in enumerate(mesh["vertex_buffers"]):
                stride = defVB[i]["stride"]
                if stride != vB["stride_byte_size"]:
                    print("Mismatched stride size, please file an issue for this item...")
                    return False
                try:
                    data = self.get(vB["file_name"]).data
                except:
                    return False
                for element in defVB[i]["elements"]:
                    if element["semantic"] == "_tfx_vb_semantic_position":
                        positions = VertexParse(data, element["type"], element["offset"], stride)
                    elif element["semantic"] == "_tfx_vb_semantic_normal":
                        normals = VertexParse(data, element["type"], element["offset"], stride)
            
            # Check that we found both a position and vertex buffer with the same length
            if (len(positions) == 0) or (len(normals) == 0) or (len(positions) != len(normals)):
                print("Mismatched position and normal vectors, exiting...")
                return False
                
            # Parse the index buffer
            indexBuffer = []
            try:
                dataBytes = self.get(mesh["index_buffer"]["file_name"]).data
            except:
                return False
            i = 0
            while i < len(dataBytes):
                indexBuffer.append(struct.unpack('<h', dataBytes[i:i+2])[0])
                i += 2
                
            parts = mesh["stage_part_list"]
            # Loop through all the parts in the mesh
            for i, part in enumerate(parts):                    
                # Check if this part has been duplicated
                ignore = False
                for j in range(i):
                    if (part["start_index"] == parts[j]["start_index"]) or (part["index_count"] == parts[j]["index_count"]):
                        ignore = True
                        
                # Skip anything meeting one of the following::
                #   duplicate part
                #   lod_category value greater than one
                if ignore or part["lod_category"]["value"] > 1:
                    continue
                
                # Get the start index and count
                start = part["start_index"]
                count = part["index_count"]
                
                # Process indexBuffer in sets of 3
                primitive_type = part["primitive_type"]
                if primitive_type == 3:
                    increment = 3
                # Process indexBuffer as triangle strip
                elif primitive_type == 5:
                    increment = 1
                    count -= 2
                # Unknown primitive define, skip this part
                else:
                    print("Unknown primitive_type, skipping this part...")
                    continue
                
                # We need to reverse the order of vertices every other iteration
                flip = False;
                
                # Create stringio for this mesh and write the header
                meshName = self.name + "_" + str(meshCount) + "_" + str(i)
                fo = io.StringIO()
                fo.write("solid " + meshName+ "\n")
                
                j = 0
                while j < count:
                    # Skip if any two of the indexBuffer match (ignoring lines or points)
                    if (indexBuffer[start+j+0] == indexBuffer[start+j+1]) or (indexBuffer[start+j+0] == indexBuffer[start+j+2]) or (indexBuffer[start+j+1] == indexBuffer[start+j+2]):
                        flip = not flip
                        j += increment
                        continue
                        
                    # Write the normal and loop start to file
                    # the normal doesn't matter for this, the order of vertices does
                    fo.write("facet normal 0.0 0.0 0.0\n")
                    fo.write("  outer loop\n")
                    
                    # flip the triangle only when using primitive_type 5
                    if flip and (primitive_type == 5):
                        # write the three vertices to the file in reverse order
                        k = 3
                        while k > 0:
                            v = positions[indexBuffer[start+j+(k-1)]]
                            v = (v + offsetConst) * scaleConst
                            fo.write("    vertex "+str(v[0])+" "+str(v[1])+" "+str(v[2])+"\n")
                            k -= 1
                    else:
                        # write the three vertices to the file in forward order
                        for k in range(3):
                            v = positions[indexBuffer[start+j+k]]
                            v = (v + offsetConst) * scaleConst
                            fo.write("    vertex "+str(v[0])+" "+str(v[1])+" "+str(v[2])+"\n")
                    
                    # Write the loop and normal end to file
                    fo.write("  endloop\n")
                    fo.write("endfacet\n")
                    
                    flip = not flip
                    j += increment
                    
                # Write stringio data to stl file
                contents = fo.getvalue()
                fStl.write(contents)
                
                # Write stringio data to zip as a separate part file
                fZip.writestr(meshName+".stl", contents)
                
                # Close stringio object
                fo.close()
                
            print("Added mesh "+str(meshCount)+" from geometry "+self.name)
                
        # Success
        return True
                
def parse(data):
    return DestinyGeometry(data)

    return