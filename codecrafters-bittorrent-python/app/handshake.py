import socket
import struct

def handshake(info_hash: bytes, ip: str = None, port: bytes = None) -> None:
        
        # the string BitTorrent protocol (19 bytes)
        protocol_str = "BitTorrent protocol".encode()

        # length of the protocol string (19 bytes)
        # len_protocol_str = chr(len(protocol_str)).encode()
        len_protocol_str = struct.pack(">B", len(protocol_str))

        # eight reserved bytes, which are all set to zero (8 bytes)
        eight_reserved_zero = 00000000
        eight_reserved_zero = eight_reserved_zero.to_bytes(8, byteorder='big')

        peer_id = "00112233445566778899".encode()   #(20 bytes) (generate 20 random byte values)

        print("protocol_str:", protocol_str, "Type:", type(protocol_str))
        print("len_protocol_str:", len_protocol_str, "Type:", type(len_protocol_str))
        print("eight_reserved_zero:", eight_reserved_zero, "Type:", type(eight_reserved_zero))
        print("peer_id:", peer_id, "Type:", type(peer_id))

        #  handshake is a message consisting of the following parts as described in the peer protocol:
        # Ensure all parts are in bytes
        handshake = len_protocol_str + protocol_str + eight_reserved_zero + info_hash + peer_id



        #  # make request to peer
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, int(port)))
            s.send(handshake)
            print(f"Peer ID: {s.recv(68)[48:].hex()}")
