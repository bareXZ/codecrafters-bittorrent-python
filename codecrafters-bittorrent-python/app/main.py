import hashlib
import sys
import traceback 
import json
import sys
import os
import numpy as np
import threading
from app.BencodeDecoder import BencodeDecoder
from app.Parse_torrent_file import Parse_torrent_file
from app.BencodeEncoder import BencodeEncoder
from app.get_peers_from_tracker  import get_peers_from_tracker 
from app.handshake  import handshake 
from app.download_piece import connect_and_download_piece




def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <command> <bencoded_value>")
        sys.exit(1)

    # print(sys.argv)

    command = sys.argv[1]
    bencoded_value = sys.argv[2].encode()

    if command == "decode":
        decoder = BencodeDecoder()
        decoded_value = decoder.decode(bencoded_value)
        print(json.dumps(decoded_value, default=decoder.bytes_to_str(decoded_value)))

    elif command == 'info':
        decoder = BencodeDecoder()
        torrent_file = sys.argv[2]
        with open(torrent_file, 'rb') as f:
            torrent_data = f.read()  # Read the entire file into a bytes object
            try:
                # gives dict with all key abd values
                parsed_torrent = Parse_torrent_file(torrent_data)
                print(f'Tracker URL: {parsed_torrent['announce']}')
                print(f'Length: {parsed_torrent['info']['length']}')
                # Convert 'pieces' to bytes
                parsed_torrent['info']['pieces'] = parsed_torrent['info']['pieces'].encode('latin-1')
                print(f"Piece Length: {parsed_torrent['info']['piece length']}")
                encoded_info = BencodeEncoder.encode(parsed_torrent['info'])
                # Calculate the hash and convert to hexadecimal
                info_hash = hashlib.sha1(encoded_info).hexdigest()
                print(f"Info Hash: {info_hash}")

                # For torrent files, each piece hash is stored as 20 bytes, so the first 20 bytes 
                # correspond to the first piece hash, the next 20 to the second, and so on.
                # each is converted to  Hexadecimal Representation:
                each_hash : int  = 20
                print('Piece Hashes:')
                for i in range(0,len(parsed_torrent['info']['pieces']),20):
                    print(parsed_torrent['info']['pieces'][i : i + each_hash].hex())
                    each_hash+=i
    

            except Exception as e:
                print(f"Decoding error: {e}")
                traceback.print_exc() 

    elif command == 'peers':
        torrent_file = sys.argv[2]
        with open(torrent_file,'rb') as f:
            torrent_data = f.read()  # Read the entire file into a bytes object
        parsed_torrent = Parse_torrent_file(torrent_data)
        parsed_torrent['info']['pieces'] = parsed_torrent['info']['pieces'].encode('latin-1')
        encoded_info = BencodeEncoder.encode(parsed_torrent['info'])

        # this is NOT the hexadecimal representation, which is 40 bytes long
        # info_hash: the info hash of the torrent
        info_hash = hashlib.sha1(encoded_info).digest()
        peer_id = "00112233445566778899"  # (20 bytes) (generate 20 random byte values)
        port = 6881
        uploaded = 0
        downloaded = 0
        left = parsed_torrent['info']['length']
        compact =  1
        tracker_url = parsed_torrent["announce"]


        parsed_torrent2 = get_peers_from_tracker(info_hash, peer_id, port, uploaded, 
                                                 downloaded, left, compact, tracker_url)

        
        # Each peer is represented using 6 bytes. The first 4 bytes are the peer's IP address and the last 2 bytes 
        # are the peer's port number.
        for i in range(0, len(parsed_torrent2['peers'].encode('latin1')), 6):
            peer = parsed_torrent2['peers'].encode('latin1')[i : i + 6]
            ip_address = f"{peer[0]}.{peer[1]}.{peer[2]}.{peer[3]}"
            port = int.from_bytes(peer[4:], byteorder="big", signed=False)
            print(f"{ip_address}:{port}")


    elif command == "handshake":
        torrent_file = sys.argv[2]
        (ip, port) = sys.argv[3].split(":")
        with open(torrent_file,'rb') as f:
            torrent_data = f.read()  # Read the entire file into a bytes object
        parsed_torrent = Parse_torrent_file(torrent_data)
        parsed_torrent['info']['pieces'] = parsed_torrent['info']['pieces'].encode('latin-1')
        encoded_info = BencodeEncoder.encode(parsed_torrent['info'])
        # this is NOT the hexadecimal representation, which is 40 bytes long
        # info_hash: the info hash of the torrent
        # sha1 infohash (20 bytes) (NOT the hexadecimal representation, which is 40 bytes long)
        info_hash = hashlib.sha1(encoded_info).digest()
        handshake(info_hash,ip, port)
     
    elif command == "download_piece":

        output_file = sys.argv[3]  # Output file path
        piece_index = int(sys.argv[5])  # Get the index of the piece to download
        torrent_file = sys.argv[4]

        # Read and parse the torrent file
        with open(torrent_file, 'rb') as f:
            torrent_data = f.read()
        
        parsed_torrent = Parse_torrent_file(torrent_data)
        parsed_torrent['info']['pieces'] = parsed_torrent['info']['pieces'].encode('latin-1')
        encoded_info = BencodeEncoder.encode(parsed_torrent['info'])

        # Compute info hash
        info_hash = hashlib.sha1(encoded_info).digest()
        peer_id = "00112233445566778899".encode()  # 20 random byte peer ID
        port = 6881
        uploaded = 0
        downloaded = 0
        left = parsed_torrent['info']['length']
        compact = 1
        tracker_url = parsed_torrent["announce"]

        parsed_torrent2 = get_peers_from_tracker(info_hash, peer_id, port, uploaded, downloaded,
                                                  left, compact, tracker_url)

        peers = []

        # Extract peers
        for i in range(0, len(parsed_torrent2['peers'].encode('latin1')), 6):
            peer = parsed_torrent2['peers'].encode('latin1')[i: i + 6]
            ip_address = f"{peer[0]}.{peer[1]}.{peer[2]}.{peer[3]}"
            port = int.from_bytes(peer[4:], byteorder="big", signed=False)
            peers.append((ip_address, port))
            print(f"Peer: {ip_address}:{port}")

        if not peers:
            raise RuntimeError("No peers available to download the piece.")

        # Connect to the first peer
        ip_address, port = peers[0]  # You could implement a more robust peer selection mechanism
        # Pass these variables to download_piece
        default_piece_length = parsed_torrent['info']['piece length']
        total_file_length = parsed_torrent['info']['length']

        # In the connect_and_download_piece call
        connect_and_download_piece(ip_address, port, piece_index, info_hash, output_file, 
                                   total_file_length, default_piece_length)


    elif command == "download":
        output_file = sys.argv[3]  # Output file path
        torrent_file = sys.argv[4]

            # Read and parse the torrent file
        with open(torrent_file, 'rb') as f:
            torrent_data = f.read()
        
        parsed_torrent = Parse_torrent_file(torrent_data)
        parsed_torrent['info']['pieces'] = parsed_torrent['info']['pieces'].encode('latin-1')
        encoded_info = BencodeEncoder.encode(parsed_torrent['info'])


        # Compute info hash
        info_hash = hashlib.sha1(encoded_info).digest()
        peer_id = "00112233445566778899".encode()  # 20 random byte peer ID
        port = 6881
        uploaded = 0
        downloaded = 0
        left = parsed_torrent['info']['length']
        compact = 1
        tracker_url = parsed_torrent["announce"]

        parsed_torrent2 = get_peers_from_tracker(info_hash, peer_id, port, uploaded, downloaded,
                                                  left, compact, tracker_url)
        peers = []

        # Extract peers
        for i in range(0, len(parsed_torrent2['peers'].encode('latin1')), 6):
            peer = parsed_torrent2['peers'].encode('latin1')[i: i + 6]
            ip_address = f"{peer[0]}.{peer[1]}.{peer[2]}.{peer[3]}"
            port = int.from_bytes(peer[4:], byteorder="big", signed=False)
            peers.append((ip_address, port))
            print(f"Peer: {ip_address}:{port}")

        if not peers:
            raise RuntimeError("No peers available to download the piece.")

        # Connect to the first peer
        ip_address, port = peers[0]  # You could implement a more robust peer selection mechanism
        # Pass these variables to download_piece
        default_piece_length = parsed_torrent['info']['piece length']
        total_file_length = parsed_torrent['info']['length']
        total_peices = int(len(parsed_torrent["info"]["pieces"]) / 20)

        all_peices = []
        i=0
        for x in range(total_peices) :
            piece_index = x
            piece_file_name : str = "peice" + str(piece_index)
            # In the connect_and_download_piece call
            peice_data = connect_and_download_piece(ip_address, port, piece_index, info_hash, piece_file_name, 
                                    total_file_length, default_piece_length)
            
            all_peices.append(peice_data)

        with open(output_file, "ab") as result_file:
            for piecefile in all_peices:
                with open(piecefile, "rb") as piece_file:
                    result_file.write(piece_file.read())
                    # os.remove(piecefile)



    else:
        raise NotImplementedError(f"Unknown command {command}")

if __name__ == "__main__":
    main()