import http.server
import socketserver
import ssl

PORT = 80
CERTFILE = "cert_mate_2.crt"
KEYFILE = "private_mate_2.pem"

Handler = http.server.SimpleHTTPRequestHandler

class MyHandler(Handler):
    def handle(self):
        print("Received a packet!")
        super().handle()


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERTFILE, keyfile=KEYFILE)

httpd = socketserver.TCPServer(("", PORT), MyHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Serving on port", PORT)
httpd.serve_forever()
