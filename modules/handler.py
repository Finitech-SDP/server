import logging
import socket
import socketserver

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
        self.robot_sock = self.wait_until_connected_to_robot()
        protocol.send_message(self.request, message=b"CONNECTED")

        try:
            while True:
                try:
                    msg = protocol.receive_message(sock=self.request)
                    logging.debug(f"Received: {msg.decode('ascii', errors='ignore')}")
                    self.handle_message(msg)
                except BrokenPipeError:
                    break  # Peer has closed the connection
        finally:
            self.robot_sock.close()

    def handle_message(self, msg: bytes):
        if not msg.startswith(b"AUTO"):
            protocol.send_message(sock=self.robot_sock, message=msg)
            return

        AUTO, ROBOT, robot_row, robot_col, CAR, car_row, car_col, mode = msg.split()
        if not (AUTO == b"AUTO" and ROBOT == b"ROBOT" and CAR == b"CAR" and mode in [b"DELIVER", b"PARK"]):
            logging.warning(f"Unknown AUTO message: {msg.decode('ascii', errors='ignore')}")
            return

        plan = deliberate((int(robot_row), int(robot_col)), (int(car_row), int(car_col), mode))
        commands = translate(plan)
        for command in commands:
            protocol.send_message(self.robot_sock, message=command)
            msg_maybe = protocol.receive_message(self.request, timeout=6)
            if msg_maybe is not None:
                print("CRYING RN", msg_maybe)
                self.handle_message(msg_maybe)
                return

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
