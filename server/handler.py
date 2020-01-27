from socketserver import BaseRequestHandler

import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)s\t%(message)s\n\tFile \"%(pathname)s\", line %(lineno)d, in %(funcName)s"
)


class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        logging.info("new connection from %s", self.request.getpeername())

        while True:
            header = self.request.recv(5)
            msg_type = header[0]
            msg_len = int.from_bytes(header[1:5], byteorder="big")

            if msg_type != 1:
                logging.critical("unknown message type: %d" % (msg_type,))
                logging.critical("terminating connection")
                break

            msg = self.request.recv(msg_len)

            # log
            logging.info("RECEIVED: %s" % (msg, ))
            # echo back!
            self.request.sendall(b"%s%s%s" % (b"\x01", len(msg).to_bytes(4, byteorder="big"), msg))
