from typing import Dict, List, Tuple, Optional

import requests

from config import PLANNER_HOST


def deliberate(robot_tuple: Tuple[int, int], car_tuple: Tuple[int, int, str]) -> Optional[List[List[str]]]:
    robot_row, robot_col = robot_tuple
    car_row, car_col, mode = car_tuple

    if mode == b"PARK":
        car_param = "parkCar"
    elif mode == b"DELIVER":
        car_param = "deliverCar"
    else:
        raise Exception(f"Unknown mode: {mode}")

    answer = requests.get(
        f"http://{PLANNER_HOST}/plan?robot={robot_row},{robot_col}&{car_param}={car_row},{car_col}"
    ).json()

    if answer["plan"] is None:
        return None

    plan = []
    for step in answer["plan"]:  # type: str
        action, *args = step.strip("()").split()
        plan.append([action, *args])

    return plan


def translate(plan: List[List[str]]) -> List[bytes]:
    table = {
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

    commands = []
    for step in plan:
        action, *args = step
        subcommands = table[action]
        commands.extend(subcommands)

    return commands
