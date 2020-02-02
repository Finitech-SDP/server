import logging
import socket
import socketserver

from modules import protocol


class TCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        self.client_host = client_address[0]
        self.client_port = client_address[1]

        super().__init__(request, client_address, server)

    def setup(self):
        logging.info(f"Client at {self.client_host}:{self.client_host} connected")

    def finish(self):
        logging.info(f"Client at {self.client_host}:{self.client_port} disconnected")

    def handle(self) -> None:
        logging.info("Excepting CONNECT command...")
        msg = protocol.receive_message(sock=self.request)
        logging.debug(f"Received {msg}")

        msg = msg.decode("ascii")

        command, host, port = msg.split()
        assert command == "CONNECT"
        port = int(port)

        logging.info(f"Connecting to {host}:{port}")

        robot_sock = self.easy_connect(host, port)

        while True:
            try:
                msg = protocol.receive_message(sock=self.request)
            except BrokenPipeError:
                break  # Peer has closed the connection

            logging.info(f"Received: {msg.decode('utf-8', errors='ignore')}")

            tokens = msg.split()
            command = tokens[0]
            power = int(tokens[1])
            degrees = int(tokens[2])
            duration = 1000

            if command == b"N":
                protocol.send_message(robot_sock, b"F %d %d" % (power, duration))
            elif command == b"S":
                protocol.send_message(robot_sock, b"B %d %d" % (power, duration))
            elif command == b"NE":
                protocol.send_message(robot_sock, b"FR %d %d" % (power, duration))
            elif command == b"NW":
                protocol.send_message(robot_sock, b"FL %d %d" % (power, duration))
            elif command == b"SE":
                protocol.send_message(robot_sock, b"BR %d %d" % (power, duration))
            elif command == b"SW":
                protocol.send_message(robot_sock, b"BL %d %d" % (power, duration))
            elif command == b'AR':
                protocol.send_message(robot_sock, b"RA %d" % (degrees,))
            elif command == b"CR":
                protocol.send_message(robot_sock, b"RC %d" % (degrees,))
            else:
                logging.warning(f"Unknown Command: {msg}")
                continue

            protocol.send_message(sock=self.request, message=msg)

    def easy_connect(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return s
