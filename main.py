import logging
import socketserver

import config
from modules import handler, util

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s  %(message)s",
)


def main() -> None:
    with socketserver.TCPServer(
        (config.HOST, config.PORT), handler.TCPHandler
    ) as server:
        local_ip = util.get_ip()

        logging.info(
            f"Server listening on {local_ip}:{config.PORT}, use ctrl+c to stop"
        )

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")


if __name__ == "__main__":
    main()
