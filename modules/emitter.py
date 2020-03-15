import asyncio
import logging
import json
from typing import Any, Dict, List, Optional

import websockets

wss = []  # type: List[websockets.WebSocketServerProtocol]


async def emit(event: str, data: Optional[Dict[str, Any]] = None):
    data = {} if data is None else data
    for ws in wss:
        try:
            await asyncio.wait_for(ws.send(json.dumps({"event": event, "data": data})), timeout=1)
        except asyncio.TimeoutError:
            logging.warning("emitter: WS send timeout: %s", ws)
