import curses
import socket
import sys
import threading
from concurrent import futures
from typing import Any, Tuple

from modules import protocol
from modules.util import get_ip

LOCK = threading.Lock()
disconnected = False


def read_line(sock: socket.socket, input_win, convo_win) -> None:
    out_counter = 0

    while True:
        msg = input_win.getstr(0, 0)
        if disconnected:
            return

        try:
            protocol.send_message(sock, msg)
        except BrokenPipeError:
            print_curses_disconnect(convo_win)
            return

        with LOCK:
            convo_win.addstr(b"<< %3d \xe2\x94\x82 %s\n" % (out_counter, msg))
            out_counter += 1
            convo_win.refresh()

            input_win.clear()


def read_socket(sock: socket.socket, convo_win) -> None:
    global disconnected
    counter = 0

    while True:
        try:
            msg = protocol.receive_message(sock)
        except BrokenPipeError:
            disconnected = True
            print_curses_disconnect(convo_win)
            return

        with LOCK:
            convo_win.standout()
            convo_win.addstr(b">> %3d " % (counter,))
            convo_win.standend()
            convo_win.addstr(b"\xe2\x94\x82 %s\n" % (msg,))
            convo_win.refresh()

            counter += 1


def print_curses_disconnect(convo_win) -> None:
    convo_win.standout()
    convo_win.addstr(b"\n---- DISCONNECTED ----\n")
    convo_win.standend()
    convo_win.refresh()


def start_curses_windows() -> Tuple[Any, Any]:
    root_win = curses.initscr()
    root_win.clear()

    convo_win = root_win.derwin(curses.LINES - 2, curses.COLS - 1, 0, 0)
    convo_win.scrollok(True)
    convo_win.leaveok(True)
    convo_win.clear()
    convo_win.addstr("Finitech netcat\n")
    convo_win.refresh()

    input_win = root_win.derwin(1, curses.COLS - 1, root_win.getmaxyx()[0] - 1, 0)

    return convo_win, input_win


def main() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # TODO: use argparse
    if len(sys.argv) >= 4 and sys.argv[3] == "listen":
        port = int(sys.argv[2])
        s.bind((sys.argv[1], port))
        s.listen(1)

        print(f"Listening on {get_ip()}:{port}")

        sock = s.accept()[0]
        s.close()
    else:
        sock = s
        sock.connect((sys.argv[1], int(sys.argv[2])))

    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    try:
        convo_win, input_win = start_curses_windows()

        with futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(read_line, sock, input_win, convo_win),
            executor.submit(read_socket, sock, convo_win)
    except KeyboardInterrupt:
        pass  # TODO: at the moment need to <C-c> twice + we get a stacktrace
    finally:
        s.close()
        curses.endwin()


if __name__ == "__main__":
    main()
