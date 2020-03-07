HOST = "0.0.0.0"
PORT = 7777
PLANNER_HOST = "127.0.0.1:8000"
# Interfaces are tried in order!
#   tun0:
#     OpenVPN
#   wlp2s0:
#     Bora's WiFi interface
#
# Feel free to add yours. =)
INTERFACES = ["tun0", "wlp2s0"]
