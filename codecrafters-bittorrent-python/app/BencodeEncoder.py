"""  
We have two possible approaches:

Single Method Approach: Create a single method to handle the encoding of dictionaries. Inside this method, use 
conditional statements to check the type of each key or value (e.g., str, int, dict, or bytes) and apply the 
corresponding encoding logic. 

Versatile Class Approach: Build a more modular class with separate methods for encoding str, int, 
dict, or bytes. In this approach, recursion would be used to handle nested structures, such as lists containing 
str, int, dict, etc., or dictionaries with complex, nested elements. This approach is more flexible and scalable.
"""

# encodes datastructures like dict , list , string , int back to bencoded format
class BencodeEncoder:  
    @staticmethod
    def encode(data):
        if isinstance(data,str):
            return f"{len(data)}:{data}".encode()
        elif isinstance(data,int):
            return f"i{data}e".encode()
        elif isinstance(data,list):
            str_lst = "l".encode()
            end_lst = "e".encode()
            for elmnt in data:
                str_lst+=BencodeEncoder.encode(elmnt)
            finl_lst = str_lst + end_lst
            return finl_lst        
        elif isinstance(data,dict):
            str_dict = "d".encode()
            end_dict = "e".encode()
            # has to be sorted lexographically to correctly hash it later 
            for key , val in sorted(data.items()):
                str_dict += BencodeEncoder.encode(key)
                str_dict += BencodeEncoder.encode(val)
            return str_dict+end_dict
        
        # handling binary data in bencoding, particularly for the 'pieces' field in torrent files
        elif isinstance(data,bytes):
            return f"{len(data)}:".encode() + data

        else:
            raise ValueError(f"Cannot encode {type(data)}")