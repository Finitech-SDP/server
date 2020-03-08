import asyncio
import enum
import logging
import json
from typing import Any, Dict, List, Optional

from modules.tcpserver import Robot
from modules.planning import deliberate, translate
from main import Coordinator


class TCPHandler:
    @enum.unique
    class State(enum.Enum):
        START = enum.auto()
        ROBOT = enum.auto()
        APP = enum.auto()
        DISCONNECTED = enum.auto()

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, coordinator: Coordinator):
        self.reader = reader
        self.writer = writer
        self.coordinator = coordinator
        self.robot = None
        self.remote_host, self.remote_port = self.writer.get_extra_info("peername")
        self.state = self.State.START

    async def run(self):
        logging.info("New TCP Connection: %s:%d", self.remote_host, self.remote_port)

        while True:
            try:
                msg = await self.receive_json_message()
                await self.handle_message(msg)
            except asyncio.streams.IncompleteReadError:
                self.state = self.State.DISCONNECTED
                logging.warning("Peer disconnected")
                break  # Peer has closed the connection

    async def handle_message(self, message: Dict[str, Any]) -> None:
        state_handlers = {
            self.State.START: self.handle_START_message,
            self.State.APP: self.handle_APP_message,
            self.State.ROBOT: self.handle_ROBOT_message,
        }
        handler = state_handlers[self.state]
        await handler(message["TAG"], message["DATA"])

    async def handle_START_message(self, tag: str, data: Dict[str, Any]):
        if tag != "IAM":
            logging.warning("First message is not IAM but %s", tag)
            return

        if data["me"] == "ROBOT":
            await self.send_json_message({
                "TAG": "IAM-ACK",
                "DATA": {}
            })
            robot = Robot(data["id"], data["name"], self)
            self.coordinator.robots[robot.id] = robot
            self.state = self.State.ROBOT
        elif data["me"] == "APP":
            await self.send_json_message({
                "TAG": "IAM-ACK",
                "DATA": {}
            })
            self.state = self.State.APP
        else:
            logging.warning("Unknown IAM me: %s", data["me"])

    async def handle_APP_message(self, tag: str, data: Dict[str, Any]):
        tag_handlers = {
            "LIST-ROBOTS": self.handle_APP_LIST_ROBOTS,
            "SELECT-ROBOT": self.handle_APP_SELECT_ROBOT,
            "RELAY-ASCII": self.handle_APP_RELAY_ASCII,
            "AUTO": self.handle_APP_AUTO,
        }
        handler = tag_handlers[tag]
        await handler(data)

    async def handle_APP_LIST_ROBOTS(self, data: Dict[str, Any]):
        await self.send_json_message({
            "TAG": "LIST-ROBOTS-RES",
            "DATA": {
                "robots": [{
                    "id": robot.id,
                    "name": robot.name,
                    "isControlled": robot.controller_handler is not None
                } for robot in self.coordinator.robots.values()]
            }
        })

    async def handle_APP_SELECT_ROBOT(self, data: Dict[str, Any]):
        robot_id = data["id"]
        robot = self.coordinator.robots[robot_id]
        if robot.controller_handler is not None:
            robot.controller_handler.robot = None

        self.robot = robot
        robot.controller_handler = self
        await self.send_json_message({
            "TAG": "SELECT-ROBOT-ACK",
            "DATA": {}
        })

    async def handle_APP_RELAY_ASCII(self, data: Dict[str, Any]):
        if self.robot is None:
            await self.send_json_message({
                "TAG": "RELAY-ASCII-NACK",
                "DATA": {
                    "error": "no robot is selected",
                }
            })
            return

        # This is an example of emitting websocket events for Theodor
        for ws in self.coordinator.websockets:
            try:
                await ws.send(data["message"] + "\n")
            except:
                logging.exception("WebSocket send exception")
                continue

        await self.robot.handler.send_message(data["message"].encode("ascii"))
        await self.send_json_message({
            "TAG": "RELAY-ASCII-ACK",
            "DATA": {},
        })

    async def handle_APP_AUTO(self, data: Dict[str, Any]):
        robot_row, robot_col = data["robotPosition"]["row"], data["robotPosition"]["column"]
        car_row, car_col = data["carPosition"]["row"], data["carPosition"]["column"]
        mode = data["mode"]

        if self.robot is None:
            await self.send_json_message({
                "TAG": "AUTO-NACK",
                "DATA": {
                    "error": "no robot is selected"
                }
            })
            return

        plan = deliberate((int(robot_row), int(robot_col)), (int(car_row), int(car_col), mode))
        if plan is None:
            logging.warning("NO PLAN FOUND")
            return
        elif len(plan) == 0:
            logging.warning("PLAN IS EMPTY [], what??")
            return

        commands = translate(plan)
        for command in commands:
            await self.robot.handler.send_message(command)
            msg_maybe = await self.receive_json_message(timeout=6)
            if msg_maybe is not None:
                await self.handle_message(msg_maybe)
                return

        await self.send_json_message({
            "TAG": "AUTO-ACK",
            "DATA": {},
        })

    async def handle_ROBOT_message(self, tag: str, data: Dict[str, Any]):
        print("ROBOT SAID", tag, data)
        raise NotImplementedError()

    async def send_json_message(self, message: Dict[str, Any]) -> None:
        await self.send_message(json.dumps(message).encode("ascii"))

    async def send_message(self, message: bytes) -> None:
        self.writer.write(b"%s%s%s" % (b"\x01", len(message).to_bytes(4, byteorder="big"), message))
        await self.writer.drain()

    async def receive_json_message(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        msg = await self.receive_message(timeout)
        if msg is None:
            return None
        else:
            return json.loads(msg.decode("ascii"))

    async def receive_message(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        :param timeout: Timeout until the first byte, NOT THE WHOLE MESSAGE.
        :return: The message or None on timeout.
        """
        assert timeout is None or timeout > 0

        try:
            type_header = await asyncio.wait_for(self.reader.readexactly(1), timeout=timeout)
        except asyncio.TimeoutError:
            return None

        length_header = await self.reader.readexactly(4)
        length = int.from_bytes(length_header, byteorder="big")
        msg = await self.reader.readexactly(length)
        return msg
