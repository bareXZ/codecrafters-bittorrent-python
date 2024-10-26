import requests
from app.Parse_torrent_file import Parse_torrent_file




def get_peers_from_tracker(info_hash: bytes, peer_id: str, port: int, uploaded: int, downloaded: int, left: int, 
                  compact: int, tracker_url: str):


    # GET request to tracker
    params = {
        "info_hash": info_hash,
        "peer_id": peer_id,
        "port": port,
        "uploaded": uploaded,
        "downloaded": downloaded,
        "left": left,
        "compact": compact,
    }

    torrent_response = requests.get(tracker_url, params)

    # Parse the tracker response
    parsed_torrent2 = Parse_torrent_file(torrent_response.content)

    return  parsed_torrent2
