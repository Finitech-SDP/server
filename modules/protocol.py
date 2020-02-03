from typing import Union
import socket


def send_message(sock: socket.socket, message: Union[bytearray, bytes]) -> None:
    sock.sendall(
        b"%s%s%s" % (b"\x01", len(message).to_bytes(4, byteorder="big"), message)
    )


def receive_message(sock: socket.socket) -> bytearray:
    type_header = recv_all(sock, 1)
    length_header = recv_all(sock, 4)
    length = int.from_bytes(length_header, byteorder="big")
    msg = recv_all(sock, length)

    return msg


def recv_all(sock: socket.socket, n: int) -> bytearray:
    """
        Receive until n bytes are fully received.
    """

    buffer = bytearray()

    while len(buffer) < n:
        r = sock.recv(n - len(buffer))

        if r == b"":
            raise BrokenPipeError("Peer has closed the connection")

        buffer += r

    return buffer
