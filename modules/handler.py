import logging
import socket
import socketserver
import time

from modules import protocol
from modules.planning import deliberate, translate


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

                if msg.startswith(b"AUTO"):
                    AUTO, ROBOT, robot_row, robot_col, CAR, car_row, car_col, mode = msg.split()
                    if not (AUTO == b"AUTO" and ROBOT == b"ROBOT" and CAR == b"CAR" and mode in [b"DELIVER", b"PARK"]):
                        logging.warning(f"Unknown AUTO message: {msg.decode('ascii', errors='ignore')}")
                        continue

                    plan = deliberate((int(robot_row), int(robot_col)), (int(car_row), int(car_col), mode))
                    commands = translate(plan)
                    for command in commands:
                        protocol.send_message(sock=robot_sock, message=command)
                        time.sleep(6)  # FIXME: cannot react to STOP commands while sleeping!
                else:
                    protocol.send_message(sock=robot_sock, message=msg)
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
