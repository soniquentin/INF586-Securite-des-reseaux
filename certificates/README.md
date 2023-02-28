# Certificates

## Basic encryption with OpenSSL

### OpenSSL commands

We use OpenSSL tool to encryption. The following command in the shell generate private.pem that contains a private key :
```
$ openssl genrsa -out private.pem 2048
```
Extract the public key :
```
$ openssl rsa -in private.pem -pubout -out public.pem
```

### Illustration of the exercise

The exercise can be drawn as follow :
![Exercise 1](img/exercice1.png)

### The server.py and client.py files

The exercise involves 6 files :
* `server.py` : the server program
* `client.py` : the client program
* `private.pem` : the private key generated by the server using the OpenSSL command above
* `public.pem` : the public key generated by the server using the OpenSSL command above
* `file_to_send.txt` : file example that the client wants to send to the server
* `file_received.txt` : file written by the server, decrypting the data sent by the client

NB : `file_to_send.txt` and `file_received.txt` must be identical, otherwise the exercice is not correct and there is an error somewhere.
