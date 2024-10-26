
from app.BencodeDecoder import BencodeDecoder


# reads in a torent file in bencoded form and decodes it into readable dict , , strings , int and lists
def Parse_torrent_file(torrent_data):
    # Example: Decode the bytes as 'latin-1' -> THis decode wont cause Data loss
    torrent_decoded_data = torrent_data.decode('latin-1')
    torrent_file_decoder = BencodeDecoder()
    torrent_file_decoder.data = torrent_decoded_data  # Access or modify self.data
    return torrent_file_decoder._decode_dict() # call the dict method , as I already Know the output will be parsed as dict