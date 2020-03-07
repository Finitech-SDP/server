import asyncio
import logging

import websockets

import config
from modules import handler, util

local_ip, interface = None, None

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s  %(message)s",
)

robots = {}

async def tcp_handler_entrypoint(reader, writer):
    tcp_handler = handler.TCPHandler(reader, writer, robots)
    await tcp_handler.run()


async def ws_handler_entrypoint(websocket, path):
    async for message in websocket:
        await websocket.send(message)


async def ws_main():
    logging.info("WebSockets handler is listening on %s:%d using %s", local_ip, config.WS_PORT, interface)
    await websockets.serve(ws_handler_entrypoint, config.HOST, config.WS_PORT)


async def tcp_main():
    logging.info("TCP handler is listening on %s:%d using %s", local_ip, config.TCP_PORT, interface)
    server = await asyncio.start_server(tcp_handler_entrypoint, config.HOST, config.TCP_PORT)
    await server.wait_closed()


def main():
    global local_ip, interface
    local_ip, interface = util.get_ip_interface()
    util.update_dynamic_dns(local_ip)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        ws_main(),
        tcp_main()
    ))
    loop.close()


if __name__ == "__main__":
    main()
