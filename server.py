import logging
import socketserver

import config
from modules.handler import TCPHandler

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s  %(message)s",
)


def main() -> None:
    with socketserver.TCPServer((config.HOST, config.PORT), TCPHandler) as server:
        logging.info(
            f"Server listening on {config.HOST}:{config.PORT}, use ctrl+c to stop"
        )

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")


if __name__ == "__main__":
    main()
