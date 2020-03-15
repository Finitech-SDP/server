import enum
import logging
from typing import Dict, List, Optional, Tuple

import aiohttp
import aiohttp.client_exceptions

from config import PLANNER_HOST

HTTP_SESSION = None
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
) -> Optional[List[str]]:
    global HTTP_SESSION
    if HTTP_SESSION is None:
        HTTP_SESSION = aiohttp.ClientSession()

    robot_row, robot_col = robot_tuple
    car_row, car_col, mode = car_tuple

    try:
        car_param = RequestMode[mode].value
    except KeyError:
        raise Exception(f"Unknown mode: {mode}")

    actions = []
    try:
        async with HTTP_SESSION.get(
            f"http://{PLANNER_HOST}/plan?robot={robot_row},{robot_col}&{car_param}={car_row},{car_col}"
        ) as resp:
            answer = await resp.json()
            if answer["plan"] is None:
                logging.warning("NO PLAN FOUND")
                return None

            for step in answer["plan"]:  # type: str
                action, *args = step.strip("()").split()
                actions.append(action)
    except aiohttp.client_exceptions.ClientConnectionError:
        logging.warning("COULD NOT CONNECT TO PLANNER")
        return None
    return actions


def translate(actions: List[str]) -> List[bytes]:
    commands = []
    for action in actions:
        commands.append(*TRANSLATION_TABLE[action])
    return commands
