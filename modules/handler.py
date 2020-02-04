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
        robot_sock = self.wait_until_connected_to_robot()
        protocol.send_message(self.request, message=b"CONNECTED")

        try:
            while True:
                try:
                    msg = protocol.receive_message(sock=self.request)
                except BrokenPipeError:
                    break  # Peer has closed the connection

                logging.debug(f"Received: {msg.decode('ascii', errors='ignore')}")
                protocol.send_message(sock=robot_sock, message=msg)
                # protocol.send_message(sock=self.request, message=msg)
        finally:
            robot_sock.close()

    def wait_until_connected_to_robot(self) -> socket.socket:
        logging.debug("Waiting for CONNECT command...")

        connect_msg = protocol.receive_message(sock=self.request).decode(
            "ascii", errors="ignore"
        )
        logging.debug(f"Received {connect_msg}")

        command, robot_host, robot_port = connect_msg.split()
        assert command == "CONNECT"

        logging.info(
            f"Connecting client {self.client_host}:{self.client_port} "
            f"to robot {robot_host}:{robot_port}"
        )

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((robot_host, int(robot_port)))

        logging.info(f"Connected to robot {robot_host}:{robot_port}")

        return sock
