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

        try:
            while True:
                try:
                    msg = protocol.receive_message(sock=self.request)
                except BrokenPipeError:
                    break  # Peer has closed the connection

                logging.debug(f"Received: {msg.decode('ascii', errors='ignore')}")

                tokens = msg.split()
                command = tokens[0]
                power = int(tokens[1])
                degrees = int(tokens[2])
                duration = 1000

                # TODO: put either in EV3 or Android App
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
                elif command == b"AR":
                    protocol.send_message(robot_sock, b"RA %d" % (degrees,))
                elif command == b"CR":
                    protocol.send_message(robot_sock, b"RC %d" % (degrees,))
                else:
                    logging.warning(f"Unknown Command: {msg}")
                    continue

                protocol.send_message(sock=self.request, message=msg)
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

        return sock
