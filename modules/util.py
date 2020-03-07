from typing import Tuple

import netifaces
import requests

from config import INTERFACES


def update_dynamic_dns():
    my_ip, _ = get_ip_interface()
    res = requests.get("https://www.duckdns.org/update", params={
        "domains": "server-finitech",
        "token": "f3c961e4-f42f-457f-8afe-961aed9636e7",
        "ip": my_ip,
        "verbose": True,
        "clear": True
    })
    assert res.ok, res


def get_ip_interface() -> Tuple[str, str]:
    addresses = None
    interface = None
    for i in INTERFACES:
        try:
            addresses = netifaces.ifaddresses(i)[netifaces.AF_INET]
            interface = i
            break
        except ValueError:
            continue
    assert addresses is not None and len(addresses) == 1
    return addresses[0]["addr"], interface
