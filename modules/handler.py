import logging
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
        while True:
            try:
                msg = protocol.receive_message(sock=self.request)

                logging.info(f"Received: {msg.decode('utf-8', errors='ignore')}")

                protocol.send_message(sock=self.request, message=msg)
            except BrokenPipeError:
                break  # Peer has closed the connection
