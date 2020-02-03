import socket


def get_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("10.255.255.255", 1))  # we don't care about reachability

            return sock.getsockname()[0]
        except socket.error:
            return ""
