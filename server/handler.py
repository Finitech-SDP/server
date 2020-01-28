from socketserver import BaseRequestHandler

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s  %(levelname)s\t%(message)s\n\tFile "%(pathname)s", line %(lineno)d, in %(funcName)s',
)


class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        host, port = self.request.getpeername()
        logging.info("new connection from %s:%d", host, port)

        while True:
            msg = self.receive_message()

            # log
            logging.info("RECEIVED: %s" % (msg,))
            # echo back!
            self.request.sendall(
                b"%s%s%s" % (b"\x01", len(msg).to_bytes(4, byteorder="big"), msg)
            )

    def receive_message(self) -> bytes:
        type_header = self.recvall(1)
        length_header = self.recvall(4)
        length = int.from_bytes(length_header, byteorder="big")
        msg = self.recvall(length)

        return msg

    def recvall(self, n: int) -> bytes:
        buffer = bytearray()

        while len(buffer) < n:
            r = self.request.recv(n - len(buffer))
            if not r:
                raise IOError()

            buffer += r

        return buffer
