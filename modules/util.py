from typing import Tuple

import netifaces
import requests  # TODO: use aiohttp so that we have fewer libraries

import config


def update_dynamic_dns(my_ip: str):
    res = requests.get(
        "https://www.duckdns.org/update",
        params={
            "domains": config.DUCK_DNS_DOMAINS,
            "token": config.DUCK_DNS_TOKEN,
            "ip": my_ip,
            "verbose": True,
            "clear": True,
        },
    )
    assert res.ok, res


def get_ip_interface() -> Tuple[str, str]:
    addresses = None
    interface = None
    for i in config.INTERFACES:
        try:
            addresses = netifaces.ifaddresses(i)[netifaces.AF_INET]
            interface = i
            break
        except ValueError:
            continue
    assert addresses is not None and len(addresses) == 1
    return addresses[0]["addr"], interface
