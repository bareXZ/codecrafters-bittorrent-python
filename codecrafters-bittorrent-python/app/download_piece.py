import struct
import math
import socket


def receive_message(s):
        # Read the length of the message
        length_bytes = s.recv(4) # Receive the first 4 bytes to determine message length
        while len(length_bytes) < 4:
            length_bytes += s.recv(4 - len(length_bytes)) # Keep receiving until we get all 4 bytes
        
        length = int.from_bytes(length_bytes, byteorder='big')  # Big-endian   # Convert from bytes to an integer
        message = b""   
        
        # Receive the remaining message (length given by the first 4 bytes)
        while len(message) < length:
            chunk = s.recv(length - len(message))  # Receive message in chunks
            if not chunk:
                break  # Connection closed
            message += chunk

        return length_bytes + message  # Return the entire message
        
def download_piece(s, piece_index, output_file, piece_length, total_file_length, default_piece_length):
    # Calculate actual piece length for the last piece
    if piece_index == (total_file_length // default_piece_length):
        piece_length = total_file_length % default_piece_length  # Remaining bytes for the last piece
    else:
        piece_length = default_piece_length

    # Determine the Number of Blocks
    # Get number of blocks (16 KiB each)
    number_of_blocks = math.ceil(piece_length / (16 * 1024))  # 16 KiB blocks
    data = bytearray() # Buffer to store the downloaded piece

    for block_index in range(number_of_blocks):
        # 2**14 is another way of writing 16 KiB (since 2^14 = 16 * 1024 = 16384 bytes).
        # We multiply 16 KiB by the block_index to get the starting point (or offset) of the current block in the piece.
        begin = 2**14 * block_index  # 2^14 = 16 KiB
        # This line calculates how large the current block should be.
        #: We want to download 16 KiB blocks, but the last block might be smaller (if the piece size isn’t an exact multiple of 16 KiB).
        block_length = min(piece_length - begin, 2**14)
        
        # Create request for the block (ID 6)
        request_payload = struct.pack(">IBIII", 13, 6, piece_index, begin, block_length)
        s.sendall(request_payload)
        # Receive the piece message (ID 7)
        # We receive a piece message from the peer, which contains the data we requested.
        message = receive_message(s)
        if message[4] != 7:
            raise RuntimeError("Expected piece message.")
        # Append the block data (message[13:] contains the block data)
        data.extend(message[13:])

    # Write the downloaded piece to the output file
    with open(output_file, "wb") as f:
        f.write(data)
    print(f"Piece {piece_index} downloaded to {output_file}.")

    return output_file

def connect_and_download_piece(ip_address: str, port: int, piece_index,
                                info_hash: bytes, output_file: str, total_file_length: int,
                                  default_piece_length: int) -> bool:


            # Prepare the handshake
            protocol_str = "BitTorrent protocol".encode()
            len_protocol_str = struct.pack(">B", len(protocol_str))
            eight_reserved_zero = b"\x00" * 8
            handshake = len_protocol_str + protocol_str + eight_reserved_zero + info_hash + b"00112233445566778899"  # Example peer ID

            # Create a socket and connect to the peer
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip_address, port))
                s.send(handshake)

                # Receive handshake response
                # client is waiting to receive exactly 68 bytes from the peer.
                response = s.recv(68)
                if not response or response[28:48] != info_hash:  # Verify info_hash in the response
                    raise RuntimeError("Invalid handshake response from peer.")

                print("Handshake successful!")

                # Wait for bitfield message (ID 5)
                message = receive_message(s)
                if message[4] != 5:
                    raise RuntimeError("Expected bitfield message.")

                # Send interested message (ID 2)
                interested_payload = struct.pack(">IB", 1, 2)
                s.sendall(interested_payload)

                # Wait for unchoke message (ID 1)
                message = receive_message(s)
                if message[4] != 1:
                    raise RuntimeError("Expected unchoke message.")

                # Start downloading the piece
                peice_data = download_piece(s, piece_index, output_file, piece_length=None, 
                               total_file_length=total_file_length,
                                 default_piece_length=default_piece_length)
                
                return peice_data