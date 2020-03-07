import logging
import socketserver

import config
from modules import handler, util
from modules.tcpserver import MyTCPServer

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s  %(message)s",
)


def main() -> None:
    util.update_dynamic_dns()
    socketserver.TCPServer.allow_reuse_address = True
    with MyTCPServer(
        (config.HOST, config.PORT), handler.TCPHandler
    ) as server:
        local_ip, interface = util.get_ip_interface()
        logging.info(
            f"Server listening on {local_ip}:{config.PORT} using {interface}; Ctrl+C to stop"
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")


if __name__ == "__main__":
    main()
