from typing import Union, List, Any


# from decode_bencode import BencodeDecoder

# decodes bencoded structure to regular dict , strings , int and lists
class BencodeDecoder:
    def __init__(self):
        self.index : int = 0
        self.data : str

    def decode(self, bencoded_value: bytes) -> Any:
        if isinstance(bencoded_value,bytes):
            self.data = BencodeDecoder.bytes_to_str(bencoded_value)
        else:
            self.data = bencoded_value
        return self._decode_next()

    def _decode_next(self) -> Any:
        if self.data[self.index].isdigit(): # we know its a digit  here which tells length of strings
            return self._decode_string()
        elif self.data[self.index] == 'i':
            return self._decode_integer()
        elif self.data[self.index] == 'l':
            return self._decode_list()
        elif self.data[self.index] == 'd':
            # print('----')
            # print(self.data[self.index:])
            return self._decode_dict()
        
        # elif self.data[self.index] == ' ':
        #     print('dddd')
        #     exit()

        else:
            raise ValueError(f"Invalid bencoded data at index {self.index}")

    def _decode_string(self) -> str:
        # self.index: This is the starting position for the search. We start 
        # searching from the current position in the data, rather than from the beginning each time.
        colon_index = self.data.index(':', self.index)
        # we again know its a digit  here which tells length of strings
        length = int(self.data[self.index:colon_index]) # extracts the int number just before the ':"
        self.index = colon_index + 1
        # the integer extracted will help with where the string element end
        string = self.data[self.index:self.index + length]
        self.index += length # increment the index to current after the string element
        return string

    def _decode_integer(self) -> int:
        self.index += 1  # Skip 'i'
        end_index = self.data.index('e', self.index)
        integer = int(self.data[self.index:end_index])
        self.index = end_index + 1
        return integer

    def _decode_list(self) -> List[Any]:
        self.index += 1  # Skip 'l'
        result = []
        while self.data[self.index] != 'e':
            result.append(self._decode_next())
        self.index += 1  # Skip 'e'
        return result
    
    def _not_end(self) -> bool:
        return self.index < len(self.data)

    def _decode_dict(self) -> dict[Any]:
        self.index +=1  # Skip 'd'
        result = {}
        curr_key: str = "None"
        i = 0 # used for alternating between keys and its values
        while self._not_end() and self.data[self.index] != 'e':
            if i%2 ==0:
                curr_key = self._decode_next()
            else: 
                result[curr_key] =self._decode_next() 
            i+=1
            # print(result)
        self.index += 1  # Skip 'e'
        return result

    @staticmethod # bytes -> string
    def bytes_to_str(data: Union[bytes, Any]) -> Union[str, Any]:
        if isinstance(data, bytes):
            return data.decode()
        return data