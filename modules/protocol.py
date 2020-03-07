from typing import Union, Optional
import socket


def send_message(sock: socket.socket, message: Union[bytearray, bytes]) -> None:
    sock.sendall(
        b"%s%s%s" % (b"\x01", len(message).to_bytes(4, byteorder="big"), message)
    )


def receive_message(sock: socket.socket, timeout: Optional[float] = None) -> Optional[bytearray]:
    """
    :param sock:
    :param timeout: Timeout until the first byte, NOT THE WHOLE MESSAGE.
    :return:
    """
    assert timeout is None or timeout > 0

    if timeout is None:
        type_header = recv_all(sock, 1)
    else:
        sock.settimeout(timeout)
        try:
            type_header = recv_all(sock, 1)
            print("wow, ", type_header)
        except socket.timeout:
            print("TIMEOUT!")
            return None
        finally:
            sock.settimeout(None)  # put it back in blocking mode

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
