import json
import socket


class EdgeComm:
    def __init__(self, device_id):
        self.device_id = device_id
        self.master_host = "127.0.0.1"
        self.master_port = 9000

    def send_heartbeat(self, device_type):
        msg = json.dumps(
            {"type": "heartbeat", "device_id": self.device_id, "device_type": device_type}
        ).encode()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(msg, (self.master_host, self.master_port))
        except:
            pass
