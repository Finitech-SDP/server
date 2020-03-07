from typing import List, Tuple
import socketserver


class App:
    def __init__(self, addr: Tuple[str, int], name: str):
        self.addr = addr
        self.name = name


class Robot:
    def __init__(self, addr: Tuple[str, int], name: str):
        self.addr = addr
        self.name = name


class MyTCPServer(socketserver.TCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apps = []  # type: List[App]
        self.robots = []  # type: List[Robot]
