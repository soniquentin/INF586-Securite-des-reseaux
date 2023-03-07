#!/usr/bin/env python

#!/usr/bin/env python

import fcntl
import os
import socket
import ssl
import struct

from scapy.all import *


class Tunnel : 
    #type_encaps = "udp", "tcp" or "ping"
    def __init__(self, src_ip, dst_ip, src_port, dst_port, type_encaps): 
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.type_encaps = type_encaps

    
    def encapsulate(self, pkt):
        if self.type_encaps == "udp" :
            return IP(dst=self.dst_ip, src=self.src_ip)/UDP(sport=self.src_port, dport=self.dst_port)/pkt
        elif self.type_encaps == "tcp" :
            return IP(dst=self.dst_ip, src=self.src_ip)/TCP(sport=self.src_port, dport=self.dst_port)/pkt
        elif self.type_encaps == "ping" :
            return IP(dst=self.dst_ip, src=self.src_ip)/ICMP()/pkt
        else :
            print("Encapsulate format not recognized")
            exit()

    def decapsulate(self, pkt):
        if type_encaps == "udp" :
            return pkt[UDP].payload
        elif type_encaps == "tcp" :
            return pkt[TCP].payload
        elif type_encaps == "ping" :
            return pkt[ICMP].payload
        else :
            print("Decapsulate format not recognized")
            exit()


'''
/* from <linux/if_tun.h> */
#define TUNSETIFF 400454ca
#define IFF_TAP         0x0002
#define IFF_NO_PI       0x1000
struct ifreq {
  char  ifrn_name[16];
  short ifru_flags;
};
'''

iface = 'tap0'
file = io.FileIO('/dev/net/tun', 'r+')
fd = file.fileno()
fcntl.ioctl(file, 0x400454ca, struct.pack('16sH', iface.encode(), 0x2|0x1000))


# Set up SSL encryption
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Initilize the tunnel object. Format IP over UDP
tune = Tunnel(src_ip = "192.168.1.1", dst_ip = "192.168.1.2", src_port = 1234, dst_port = 5678, type_encaps = "udp")

### Only encapsulate IP over UDP
while True:
    buf = os.read(fd, 1500)
    pkt = Ether(buf)
    pkt.show()

    # Encapsulate the packet with our custom header
    enc_pkt = tune.encapsulate(pkt)
    
    with context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect(('192.168.1.2', 5678))
        s.sendall(bytes(new_pkt))
        data = s.recv(1500)

    # Decapsulate the packet
    dec_pkt = tune.decapsulate(Ether(data))
    os.read(fd, dec_pkt)