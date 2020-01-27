import socketserver

from server.handler import MyTCPHandler


def main():
    HOST, PORT = "0.0.0.0", 7777

    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()


if __name__ == "__main__":
    main()
