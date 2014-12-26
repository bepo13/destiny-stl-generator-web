import io
import struct
import numpy as np

def VertexParse(dataBytes, datatype, offset, stride):
    dataOut = []
    i = offset
    while i < len(dataBytes):
        if datatype == "_vertex_format_attribute_short4":
            dataOut.append(np.array(struct.unpack('<hhhh', dataBytes[i:i+8])))
        elif datatype == "_vertex_format_attribute_float4":
            dataOut.append(np.array(struct.unpack('<ffff', dataBytes[i:i+16])))
        else:
            print("Unknown type, please file an issue for this item...")
            return
        i += stride
            
    return dataOut
    
class DataParse:
    def __init__(self, byteData):
        self.data = io.BytesIO(byteData)
        return
    
    def seek(self, address):
        self.data.seek(address, 0)
        return
    
    def read(self, length):
        return self.data.read(length)
        
    def readString(self, length):
        return self.data.read(length).decode('utf-8').rstrip('\0')
        
    def readUTF(self):
        length = int.from_bytes(self.data.read(2), byteorder='little')
        return self.data.read(length).decode('utf-8')
    
    def readInt8(self):
        return struct.unpack('<b', self.data.read(1))[0]
    
    def readInt16(self):
        return struct.unpack('<h', self.data.read(2))[0]
    
    def readInt32(self):
        return struct.unpack('<l', self.data.read(4))[0]
    
    def readInt64(self):
        return struct.unpack('<q', self.data.read(8))[0]
    
    def readFloat(self):
        return struct.unpack('f', self.data.read(4))[0]
    
    def readVector2D(self):
        return np.array([self.readFloat(), self.readFloat()], dtype='float')
    
    def readVector3D(self):
        return np.array([self.readFloat(), self.readFloat(), self.readFloat()], dtype='float')
    
    def readVector4D(self):
        return np.array([self.readFloat(), self.readFloat(), self.readFloat(), self.readFloat()], dtype='float')