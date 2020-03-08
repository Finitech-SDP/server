import unittest
import socket
from uuid import uuid4
import json
from typing import Any, Dict

from modules.protocol import send_message, receive_message


class MyTestCase(unittest.TestCase):
    """
    MUST start the server before the test case.
    """
    HOST = "127.0.0.1"
    PORT = 7777

    def setUp(self) -> None:
        self.robot_socket = robot_socket = socket.create_connection((self.HOST, self.PORT))
        self.app_socket = app_socket = socket.create_connection((self.HOST, self.PORT))
        self.robot_id = robot_id = str(uuid4())

        # 1) Robot Connected
        self.__send_json_message(robot_socket, {
            "TAG": "IAM",
            "DATA": {"me": "ROBOT", "id": robot_id}
        })
        ack = self.__receive_json_message(robot_socket)
        self.assertEqual({
            "TAG": "IAM-ACK",
            "DATA": {}
        }, ack)

        # 2) App Connected
        self.__send_json_message(app_socket, {
            "TAG": "IAM",
            "DATA": {"me": "APP"}
        })
        ack = self.__receive_json_message(app_socket)
        self.assertEqual({
            "TAG": "IAM-ACK",
            "DATA": {}
        }, ack)

    def test_auto(self):
        """
        This takes a long time because the server sends the command and waits for n seconds.
        Will be much faster when the commands are batched and queued on the robot instead.
        :return:
        """

        app_socket = self.app_socket
        robot_socket = self.robot_socket
        robot_id = self.robot_id

        # 1) App asks for the list of robots
        self.__send_json_message(app_socket, {
            "TAG": "LIST-ROBOTS",
            "DATA": {}
        })
        ack = self.__receive_json_message(app_socket)
        self.assertEqual("LIST-ROBOTS-RES", ack["TAG"])
        self.assertIn({"id": robot_id, "name": "Bender", "isControlled": False}, ack["DATA"]["robots"])

        # 2) App selects a robot from the list by its ID
        self.__send_json_message(app_socket, {
            "TAG": "SELECT-ROBOT",
            "DATA": {
                "id": robot_id,
            }
        })
        ack = self.__receive_json_message(app_socket)
        self.assertEqual({
            "TAG": "SELECT-ROBOT-ACK",
            "DATA": {}
        }, ack)

        # 3) App enters auto mode
        self.__send_json_message(app_socket, {
            "TAG": "AUTO",
            "DATA": {
                "robotPosition": {"row": 0, "column": 2},
                "mode": "PARK",
                "carPosition": {"row": 3, "column": 1}
            }
        })

        expectations = [
            b"L  ",
            b"L  ",
            b"L  ",
            b"F  ",
            b"B  ",
            b"B  ",
            b"F  ",
            b"R  ",
            b"R  ",
            b"R  "
        ]
        for i in range(10):
            msg = receive_message(robot_socket, timeout=10)
            self.assertEqual(expectations[i], msg)

        ack = self.__receive_json_message(app_socket)
        self.assertEqual({
            "TAG": "AUTO-ACK",
            "DATA": {}
        }, ack)

    def test_relay_ascii(self):
        app_socket = self.app_socket
        robot_socket = self.robot_socket
        robot_id = self.robot_id

        # 1) App asks for the list of robots
        self.__send_json_message(app_socket, {
            "TAG": "LIST-ROBOTS",
            "DATA": {}
        })
        ack = self.__receive_json_message(app_socket)
        self.assertEqual("LIST-ROBOTS-RES", ack["TAG"])
        self.assertIn({"id": robot_id, "name": "Bender", "isControlled": False}, ack["DATA"]["robots"])

        # 2) App selects a robot from the list by its ID
        self.__send_json_message(app_socket, {
            "TAG": "SELECT-ROBOT",
            "DATA": {
                "id": robot_id,
            }
        })
        ack = self.__receive_json_message(app_socket)
        self.assertEqual({
            "TAG": "SELECT-ROBOT-ACK",
            "DATA": {}
        }, ack)

        # 3) App asks for an ASCII message to be relayed
        self.__send_json_message(app_socket, {
            "TAG": "RELAY-ASCII",
            "DATA": {
                "message": "F  ",
            }
        })
        robot_msg = receive_message(robot_socket)
        self.assertEqual(b"F  ", robot_msg)
        ack = self.__receive_json_message(app_socket)
        self.assertEqual({
            "TAG": "RELAY-ASCII-ACK",
            "DATA": {},
        }, ack)

    def doCleanups(self) -> None:
        self.robot_socket.close()
        self.app_socket.close()

    def __send_json_message(self, sock: socket.socket, message: Dict[str, Any]):
        send_message(sock, json.dumps(message).encode("ascii"))

    def __receive_json_message(self, sock: socket.socket) -> Dict[str, Any]:
        return json.loads(receive_message(sock).decode("ascii"))


if __name__ == '__main__':
    unittest.main()