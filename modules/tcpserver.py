from typing import Optional, Tuple

import modules.handler


class App:
    def __init__(self, addr: Tuple[str, int], name: str):
        self.addr = addr
        self.name = name


class Robot:
    def __init__(self, id_: str, name: str, handler: "modules.handler.TCPHandler"):
        self.id = id_
        self.name = name
        self.handler = handler
        self.controller_handler = None  # type: Optional["modules.handler.TCPHandler"]
