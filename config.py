HOST = "0.0.0.0"
WS_PORT = 8888
TCP_PORT = 7777
PLANNER_HOST = "127.0.0.1:8000"

DUCK_DNS_TOKEN = "f3c961e4-f42f-457f-8afe-961aed9636e7"
DUCK_DNS_DOMAINS = "server-finitech"

# Interfaces are tried in order!
#   tun0:
#     OpenVPN
#   wlp2s0:
#     Bora's WiFi interface
#
# Feel free to add yours. =)
INTERFACES = ["tun0", "wlp2s0"]
