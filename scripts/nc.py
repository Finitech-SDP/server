#!/usr/bin/env python3


import curses
import sys
import socket
import threading
import typing


def main(s):
    root_win = curses.initscr()
    root_win.clear()

    convo_win = root_win.derwin(curses.LINES - 2, curses.COLS - 1, 0, 0)
    convo_win.scrollok(True)
    convo_win.leaveok(True)
    convo_win.clear()
    convo_win.addstr("finitech netcat v2020-01-27\n")
    convo_win.refresh()

    input_win = root_win.derwin(1, curses.COLS - 1, root_win.getmaxyx()[0] - 1, 0)

    #
    lock = threading.Lock()

    read_line_th = threading.Thread(target=read_line, args=(lock, s, input_win, convo_win))
    read_socket_th = threading.Thread(target=read_socket, args=(lock, s, convo_win))

    read_line_th.start()
    read_socket_th.start()

    read_line_th.join()


def read_line(lock: threading.Lock, sock: socket.socket, input_win, convo_win):
    out_counter = 0

    while True:
        str = input_win.getstr(0, 0)
        sock.sendall(b"%s%s%s" % (b"\x01", len(str).to_bytes(length=4, byteorder="big"), str))

        lock.acquire(blocking=True)
        try:
            convo_win.addstr(b"<< %3d \xe2\x94\x82 %s\n" % (out_counter, str))
            out_counter += 1
            convo_win.refresh()

            input_win.clear()
        finally:
            lock.release()


def read_socket(lock: threading.Lock, sock: socket.socket, convo_win):
    counter = 0

    while True:
        data = sock.recv(1024)
        if not data:
            convo_win.standout()
            convo_win.addstr(b"\n---- DISCONNECTED ----\n")
            convo_win.standend()
            convo_win.refresh()
            return

        messages = get_messages(data)

        lock.acquire(blocking=True)
        try:
            for msg in messages:
                convo_win.standout()
                convo_win.addstr(b">> %3d " % (counter,))
                convo_win.standend()
                convo_win.addstr(b"\xe2\x94\x82 %s\n" % (msg,))
                convo_win.refresh()

                counter += 1
        finally:
            lock.release()


def get_messages(data: bytes) -> typing.List[bytes]:
    messages = []

    while data:
        type = data[0]
        length = int.from_bytes(data[1:5], byteorder="big")
        msg = data[5:5+length]
        messages.append(msg)
        data = data[5+length:]

    return messages

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((sys.argv[1], int(sys.argv[2])))
        main(s)
    except KeyboardInterrupt:
        pass
    finally:
        s.close()
        curses.endwin()
