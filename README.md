##### Table of contents
- [Some important commands](#some-important-commands)
  - [Run a quick Python server on localhost](#run-a-quick-python-server-on-localhost)
  - [Scapy](#scapy)
    - [Run scapy in the terminal as root :](#run-scapy-in-the-terminal-as-root-)
    - [Config a new TCP/UDP packet to send :](#config-a-new-tcpudp-packet-to-send-)
    - [Voir à quoi ressemble le packet :](#voir-à-quoi-ressemble-le-packet-)
    - [Send the packet :](#send-the-packet-)
  - [dig](#dig)
    - [Display important information SOA (= serial, refresh, retry, expire, negative ttl)](#display-important-information-soa--serial-refresh-retry-expire-negative-ttl)
    - [DNSSEC awareness](#dnssec-awareness)
    - [Flags Memo :](#flags-memo-)
  - [BIND9](#bind9)
    - [Check the config](#check-the-config)
    - [Run commands](#run-commands)
  - [Sniff in monitor mode on MacOS](#sniff-in-monitor-mode-on-macos)


# Some important commands



## Run a quick Python server on localhost

* Run the server on port 80
```
python3 -m http.server 80
```

* See what process is still running the server :
```
(base) quentinlao@MBP-de-Quentin test % lsof -nP -iTCP -sTCP:LISTEN | grep 8000

python3.9 77244 quentinlao    5u  IPv6 0x9ceac175dda6b5a7      0t0  TCP *:8000 (LISTEN)
```

* Kill this process :
```
(base) quentinlao@MBP-de-Quentin test % kill -9 77244

[1]  + killed     python3 -m http.server
```

## Scapy


### Run scapy in the terminal as root :
```
(qlao㉿kali)-[~] $ sudo su            
(root㉿kali)-[/home/qlao] # scapy
```

### Config a new TCP/UDP packet to send :

(S flag means _SYN_)
```       
>>> p = Ether(src='08:00:27:c4:c4:ae',dst='52:54:00:12:35:02')/IP(src='10.0.2.15',dst='104.21.5.178')/TCP(dport=80,flags='S')
```
or a DNS query : (RD = Recursion Available denotes whether recursive query support is available in the name server)
```       
>>> p = Ether(src='08:00:27:c4:c4:ae',dst='52:54:00:12:35:02')/IP(src='10.0.2.15',dst='129.104.201.59')/UDP(sport=43228, dport = 53)/DNS(rd=1,qd=DNSQR(qname="www.perdu.com"))
```

### Voir à quoi ressemble le packet :
```
>>> p.show()
```

OUTPUT :
```
###[ Ethernet ]### 
  dst       = 52:54:00:12:35:02
  src       = 08:00:27:c4:c4:ae
  type      = IPv4
###[ IP ]### 
     version   = 4
     ihl       = None
     tos       = 0x0
     len       = None
     id        = 1
     flags     = 
     frag      = 0
     ttl       = 64
     proto     = tcp
     chksum    = None
     src       = 10.0.2.15
     dst       = 104.21.5.178
     \options   \
###[ TCP ]### 
        sport     = ftp_data
        dport     = http
        seq       = 0
        ack       = 0
        dataofs   = None
        reserved  = 0
        flags     = S
        window    = 8192
        chksum    = None
        urgptr    = 0
        options   = ''
```

### Send the packet : 
_iface_ est l'interface par lequel on veut envoyer le packet.
```       
>>> sendp(p,iface='eth0')
```  

OUTPUT :
```  
.
Sent 1 packets.
```


## dig

### Display important information SOA (= serial, refresh, retry, expire, negative ttl)
* SOA can be replaced by A, AAAA, NS, ...
```
dig SOA polytechnique.edu
```
* Ask to a specific DNS (`@8.8.8.8` is Google's one // `@127.0.0.1` for localhost as DNS)
```
dig SOA @8.8.8.8 polytechnique.edu
```

OUTPUT :
```
; <<>> DiG 9.10.6 <<>> SOA @8.8.8.8 polytechnique.edu
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 24970
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;polytechnique.edu.		IN	SOA

;; ANSWER SECTION:
polytechnique.edu.	3600	IN	SOA	milou.polytechnique.fr. hostmaster.polytechnique.fr. 2023011117 86400 21600 1209600 3600

;; Query time: 36 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Sat Feb 18 15:11:15 CET 2023
;; MSG SIZE  rcvd: 115
```

### DNSSEC awareness
* Add `+dnssec` (i.e DO flag = 1 -> "Please include RRSIG with the Ressource Records") :
```
dig @8.8.8.8 +dnssec www.apinec.net
```
OUTPUT :
```
; <<>> DiG 9.10.6 <<>> @8.8.8.8 +dnssec www.apnic.net
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 37844
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 5, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags: do; udp: 512
;; QUESTION SECTION:
;www.apnic.net.			IN	A

;; ANSWER SECTION:
www.apnic.net.		21011	IN	CNAME	www.apnic.net.cdn.cloudflare.net.
www.apnic.net.		21011	IN	RRSIG	CNAME 13 3 86400 20230303053514 20230216040514 31255 apnic.net. dDLvaKTwMJv3J+K8XF7FJBJ2wMHVosLJWSWQAcUy9hsWQOnJKqzr0Rjt bHiOLN93p2TznedFDoOVM/ToUTGc7A==
www.apnic.net.cdn.cloudflare.net. 300 IN A	104.18.235.68
www.apnic.net.cdn.cloudflare.net. 300 IN A	104.18.236.68
www.apnic.net.cdn.cloudflare.net. 300 IN RRSIG	A 13 6 300 20230219152742 20230217132742 34505 cloudflare.net. quY2kFr3GDLGyd7vuUILJRFelWrSPkwNN1/Z5sxm9sAdm3VcUPo8h80a FdatA+3Nw/mcCO6dKMUQq3CKmKaI+A==

;; Query time: 34 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Sat Feb 18 15:27:42 CET 2023
;; MSG SIZE  rcvd: 332
```

* Add `+multiline` to make the output more beautiful (line returns)
* Add `+DNSKEY` to display only DNSKEY records
```
dig @8.8.8.8 +dnssec +multiline apnic.net DNSKEY 
```

OUTPUT :
```
; <<>> DiG 9.10.6 <<>> @8.8.8.8 +dnssec +multiline apnic.net DNSKEY
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 43433
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags: do; udp: 512
;; QUESTION SECTION:
;apnic.net.		IN DNSKEY

;; ANSWER SECTION:
apnic.net.		3600 IN	DNSKEY 256 3 13 (
				Y6ABoDfZ132gZrSzZNSXAvuK+CjqX2L/Wr5Z6/JF4gI0
				aPKhAX1pW2vIAAFRS8Zyvc7IgZ2wC2l8hdppwumHzg==
				) ; ZSK; alg = ECDSAP256SHA256 ; key id = 31255
apnic.net.		3600 IN	DNSKEY 257 3 13 (
				3NbLPP4IDRHT01x4y3NtKQrJ0L6yb5Gz9q7ftsX9em4v
				PnqcvCHLqMLMZdd441f3ZwsF3C0JHT0+sVj+a34KfA==
				) ; KSK; alg = ECDSAP256SHA256 ; key id = 18078
apnic.net.		3600 IN	RRSIG DNSKEY 13 2 3600 (
				20230303053514 20230216040514 18078 apnic.net.
				Iox5Wzwye2iWBfvN2P/pB62VUl8KJsJ0D9uGqdLyHUEq
				jsW6GKWlRIplo63KcOgQ1wkKPbCwhoLGe95JCduhHQ== )

;; Query time: 30 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Sat Feb 18 15:30:32 CET 2023
;; MSG SIZE  rcvd: 303
```

### Flags Memo :

* qr: the message is a response (which is the case: dig received a response to our query)
* aa: the message contains authoritative information e.g the queried server claims to be authoritative for the queried domain
* tc: the message is truncated
* rd: basically stored in the query to request the name server to do recursive (and not iterative) queries. rd is just copied in the response
* ra: set by the server to indicate if recursive querying is supported.
* cd: tell the resolver to not perform DNSSEC checks. cd is just copied in the response
* ad: indicate that the server has verified that all RRsets are authentic.


## BIND9

### Check the config

```
/usr/local/sbin/named-checkconf /etc/named.conf
```

### Run commands

Once installed :
```
sudo /usr/local/sbin/named -c /etc/named.conf -d 3 -g
```

## Sniff in monitor mode on MacOS

1. On Wireshark, activate the monitor mode _Capture > Options..._
2. Generate a WPA-PSK using [this Wireshark tool](https://www.wireshark.org/tools/wpa-psk.html) (Passphrase = password of the wifi, SSID = name of the wifi)
3. Add the WPA-PSK _Wireshark > Preferences... > Protocols > IEEE 802.11 > Edit_ and make sure that the "Enable decryption" box is checked
4. Turn off the wifi (on the new MacOS, cannot activate the monitor mode while being connected to a wifi)
5. Start capturing packets !
