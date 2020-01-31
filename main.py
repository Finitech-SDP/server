import logging
import socket
import socketserver

import config
from modules.handler import TCPHandler

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s  %(message)s",
)


def main() -> None:
    with socketserver.TCPServer((config.HOST, config.PORT), TCPHandler) as server:
        local_ip = get_ip()

        logging.info(
            f"Server listening on {local_ip}:{config.PORT}, use ctrl+c to stop"
        )

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")


# Hacky, but it works...
# TODO: is there a fix?
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # we don't care about reachability or anything really!
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except:
        ip = None
    finally:
        s.close()

    return ip


if __name__ == "__main__":
    main()
