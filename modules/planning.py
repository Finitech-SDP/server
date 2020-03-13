import collections
import enum
import logging
from typing import Dict, List, Optional, Tuple

import aiohttp

from config import PLANNER_HOST

HTTP_SESSION = aiohttp.ClientSession()
TRANSLATION_TABLE = {
    "GO-DOWN": [b"L  "],
    "GO-UP": [b"R  "],
    "GO-LEFT": [b"F  "],
    "GO-RIGHT": [b"B  "],
    "PICKUP-CAR-LEFTWARDS": [b"F  "],
    "PICKUP-CAR-RIGHTWARDS": [b"B  "],
    "PARK-CAR-LEFTWARDS": [b"F  "],
    "PARK-CAR-RIGHTWARDS": [b"B  "],
    "RETRIEVE-CAR-LEFTWARDS": [b"F  "],
    "RETRIEVE-CAR-RIGHTWARDS": [b"B  "],
    "DROPOFF-CAR-LEFTWARDS": [b"F  "],
    "DROPOFF-CAR-RIGHTWARDS": [b"B  "],
}  # type: Dict[str, List[bytes]]


@enum.unique
class RequestMode(enum.Enum):
    PARK = "parkCar"
    DELIVER = "deliverCar"


async def deliberate(
    robot_tuple: Tuple[int, int], car_tuple: Tuple[int, int, str]
) -> Optional[collections.AsyncGenerator]:
    robot_row, robot_col = robot_tuple
    car_row, car_col, mode = car_tuple

    try:
        car_param = RequestMode[mode]
    except KeyError:
        raise Exception(f"Unknown mode: {mode}")

    async with HTTP_SESSION.get(
        f"http://{PLANNER_HOST}/plan?robot={robot_row},{robot_col}&{car_param}={car_row},{car_col}"
    ) as resp:
        answer = await resp.json()

        if answer["plan"] is None:
            logging.warning("NO PLAN FOUND")
            yield None

        for step in answer["plan"]:  # type: str
            action, *args = step.strip("()").split()
            yield TRANSLATION_TABLE[action]
