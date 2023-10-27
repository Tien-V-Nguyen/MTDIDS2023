from time import sleep
import numpy as np
import sys
from datetime import datetime
from scapy.all import IP,UDP,sr1,ICMP


port_from = 0
port_to = 0
# Defining a target
if len(sys.argv) >= 4:
    # translate hostname to IPv4
    # target = socket.gethostbyname(sys.argv[1])
    ip = sys.argv[1]
    port_from = int(sys.argv[2])
    port_to = int(sys.argv[3])
else:
    print("Invalid amount of Argument")

# Add Banner
print("-" * 50)
print("Scanning Target: " + ip)
print("Scanning started at:" + str(datetime.now()))
print("-" * 50)
arr = np.arange(port_from, port_to+1)
np.random.shuffle(arr)
try:

    for port in arr:
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # socket.setdefaulttimeout(1)

        # returns an error indicator
        # result = s.connect_ex((target, port))

        packet = IP(dst=ip)/UDP(sport=10000,dport=port)/""
        ans, unans = sr1(packet,timeout=0.2)
        print(ans, unans)

        if len(ans) == 0 and len(unans) > 0:
            packet = IP(unans)
            packet.show()
            if ICMP in packet:
                print("ok")
            else:
                print("Port {} is open".format(port))
                break
        # s.close()
        # sleep(1)

except Exception as e:
    print(e)
    sys.exit()
